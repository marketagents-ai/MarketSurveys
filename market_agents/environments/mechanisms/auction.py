# double_auction.py

from datetime import datetime
import json
import logging
from typing import Any, List, Dict, Union, Type, Optional, Tuple
from pydantic import BaseModel, Field, field_validator
from market_agents.environments.environment import (
    Mechanism, LocalAction, GlobalAction, LocalObservation, GlobalObservation,
    EnvironmentStep, ActionSpace, ObservationSpace, MultiAgentEnvironment
)
from market_agents.economics.econ_models import Bid, Ask, MarketAction, Trade
import random
logger = logging.getLogger(__name__)

class MarketSummary(BaseModel):
    trades_count: int = Field(default=0, description="Number of trades executed")
    average_price: float = Field(default=0.0, description="Average price of trades")
    total_volume: int = Field(default=0, description="Total volume of trades")
    price_range: Tuple[float, float] = Field(default=(0.0, 0.0), description="Range of prices")

class AuctionAction(LocalAction):
    action: Union[Bid, Ask]

    @field_validator('action')
    def validate_quantity(cls, v):
        if v.quantity != 1:
            raise ValueError("Quantity must be 1")
        return v

    @classmethod
    def sample(cls, agent_id: str) -> 'AuctionAction':
        is_buyer = random.choice([True, False])
        random_price = random.uniform(0, 100)
        action = Bid(price=random_price, quantity=1) if is_buyer else Ask(price=random_price, quantity=1)
        return cls(agent_id=agent_id, action=action)
    
    @classmethod
    def action_schema(cls) -> Dict[str, Any]:
        return MarketAction.model_json_schema()

class GlobalAuctionAction(GlobalAction):
    actions: Dict[str, AuctionAction]

class AuctionObservation(BaseModel):
    trades: List[Trade] = Field(default_factory=list, description="List of trades the agent participated in")
    market_summary: MarketSummary = Field(default_factory=MarketSummary, description="Summary of market activity")
    waiting_orders: List[Union[Bid, Ask]] = Field(default_factory=list, description="List of orders waiting to be executed")

    def serialize_json(self) -> str:
        """Serialize the observation to JSON string, handling datetime objects"""
        return json.dumps(self.model_dump(), default=lambda x: x.isoformat() if isinstance(x, datetime) else x.model_dump() if hasattr(x, 'model_dump') else x)

class AuctionLocalObservation(LocalObservation):
    observation: AuctionObservation

    def serialize_json(self) -> str:
        """Serialize the local observation to JSON string"""
        return json.dumps({
            "agent_id": self.agent_id,
            "observation": json.loads(self.observation.serialize_json())
        })

class AuctionGlobalObservation(GlobalObservation):
    observations: Dict[str, AuctionLocalObservation]
    all_trades: List[Trade]
    market_summary: MarketSummary

    def serialize_json(self) -> str:
        """Serialize the global observation to JSON string"""
        return json.dumps({
            "observations": {
                agent_id: json.loads(obs.serialize_json())
                for agent_id, obs in self.observations.items()
            },
            "all_trades": [trade.model_dump() for trade in self.all_trades],
            "market_summary": self.market_summary.model_dump()
        })


class AuctionActionSpace(ActionSpace):
    allowed_actions: List[Type[LocalAction]] = [AuctionAction]

    @classmethod
    def get_action_schema(cls) -> Dict[str, Any]:
        return MarketAction.model_json_schema()

class AuctionObservationSpace(ObservationSpace):
    allowed_observations: List[Type[LocalObservation]] = [AuctionLocalObservation]


class DoubleAuction(Mechanism):
    max_rounds: int = Field(default=10, description="Maximum number of auction rounds")
    current_round: int = Field(default=0, description="Current round number")
    trades: List[Trade] = Field(default_factory=list, description="List of executed trades")
    waiting_bids: List[AuctionAction] = Field(default_factory=list, description="List of waiting bids")
    waiting_asks: List[AuctionAction] = Field(default_factory=list, description="List of waiting asks")
    good_name: str = Field(default="apple", description="Name of the good being traded")

    sequential: bool = Field(default=False, description="Whether the mechanism is sequential")

    def step(self, action: GlobalAuctionAction) -> EnvironmentStep:
        self.current_round += 1
        self._update_waiting_orders(action.actions)
        new_trades = self._match_orders()
        self.trades.extend(new_trades)

        market_summary = self._create_market_summary(new_trades)
        observations = self._create_observations(new_trades, market_summary)
        done = self.current_round >= self.max_rounds

        return EnvironmentStep(
            global_observation=AuctionGlobalObservation(
                observations=observations,
                all_trades=new_trades,
                market_summary=market_summary
            ),
            done=done,
            info={"current_round": self.current_round}
        )

    def _update_waiting_orders(self, actions: Dict[str, AuctionAction]):
        for agent_id, auction_action in actions.items():
            action = auction_action.action
            if isinstance(action, Bid):
                # print(f"Bid from agent {agent_id}: {action}")
                self.waiting_bids.append(auction_action)
            elif isinstance(action, Ask):
                # print(f"Ask from agent {agent_id}: {action}")
                self.waiting_asks.append(auction_action)
            else:
                logger.error(f"Invalid action type from agent {agent_id}: {type(action)}")

    def _match_orders(self) -> List[Trade]:
        trades = []
        trade_id = len(self.trades)

        # Sort bids and asks
        self.waiting_bids.sort(key=lambda x: x.action.price, reverse=True)
        self.waiting_asks.sort(key=lambda x: x.action.price)

        while self.waiting_bids and self.waiting_asks:
            bid = self.waiting_bids[0]
            ask = self.waiting_asks[0]

            if bid.action.price >= ask.action.price:
                trade_price = (bid.action.price + ask.action.price) / 2

                trade = Trade(
                    trade_id=trade_id,
                    buyer_id=bid.agent_id,
                    seller_id=ask.agent_id,
                    price=trade_price,
                    quantity=1,
                    good_name=self.good_name,
                    bid_price=bid.action.price,
                    ask_price=ask.action.price
                )
                trades.append(trade)
                trade_id += 1

                # Remove matched bid and ask
                self.waiting_bids.pop(0)
                self.waiting_asks.pop(0)
            else:
                # No more matches possible
                break

        return trades

    def _create_observations(self, new_trades: List[Trade], market_summary: MarketSummary) -> Dict[str, AuctionLocalObservation]:
        observations = {}

        # Agents with trades in this round
        participant_ids = set([trade.buyer_id for trade in new_trades] + [trade.seller_id for trade in new_trades])

        # Agents with waiting orders
        waiting_order_agents = set([bid.agent_id for bid in self.waiting_bids] + [ask.agent_id for ask in self.waiting_asks])

        all_agent_ids = participant_ids.union(waiting_order_agents)

        for agent_id in all_agent_ids:
            agent_trades = [trade for trade in new_trades if trade.buyer_id == agent_id or trade.seller_id == agent_id]
            agent_waiting_bids = [bid.action for bid in self.waiting_bids if bid.agent_id == agent_id]
            agent_waiting_asks = [ask.action for ask in self.waiting_asks if ask.agent_id == agent_id]
            agent_waiting_orders = agent_waiting_bids + agent_waiting_asks

            observation = AuctionObservation(
                trades=agent_trades,
                market_summary=market_summary,
                waiting_orders=agent_waiting_orders
            )

            observations[agent_id] = AuctionLocalObservation(
                agent_id=agent_id,
                observation=observation
            )

        return observations

    def get_global_state(self) -> Dict[str, Any]:
        return {
            "current_round": self.current_round,
            "trades": [trade.model_dump() for trade in self.trades],
            "waiting_bids": [{ "agent_id": bid.agent_id, **bid.action.model_dump() } for bid in self.waiting_bids],
            "waiting_asks": [{ "agent_id": ask.agent_id, **ask.action.model_dump() } for ask in self.waiting_asks]
        }

    def reset(self) -> None:
        self.current_round = 0
        self.trades = []
        self.waiting_bids = []
        self.waiting_asks = []

    def _create_market_summary(self, trades: List[Trade]) -> MarketSummary:
        if not trades:
            return MarketSummary()

        prices = [trade.price for trade in trades]
        return MarketSummary(
            trades_count=len(trades),
            average_price=sum(prices) / len(prices),
            total_volume=len(trades),
            price_range=(min(prices), max(prices))
        )

class AuctionMarket(MultiAgentEnvironment):
    name: str = Field(default="Auction Market", description="Name of the auction market")
    
    action_space : AuctionActionSpace = Field(default_factory=AuctionActionSpace, description="Action space of the auction market")
    observation_space : AuctionObservationSpace = Field(default_factory=AuctionObservationSpace, description="Observation space of the auction market")
    mechanism : DoubleAuction = Field(default_factory=DoubleAuction, description="Mechanism of the auction market")

