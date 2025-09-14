import asyncio
import json
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum

class AgentStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"

@dataclass
class AgentConfig:
    num_steps: int = 10
    model: str = "gpt-4"
    temperature: float = 0.7
    api_key: str = ""
    system_message: str = "You are a helpful AI assistant."

@dataclass
class AgentState:
    status: AgentStatus = AgentStatus.IDLE
    current_step: int = 0
    memory_usage: float = 0.0
    output: str = ""
    last_error: Optional[str] = None
    start_time: Optional[float] = None

class HumanoidAgent:
    def __init__(self, config: Optional[AgentConfig] = None):
        self.config = config or AgentConfig()
        self.state = AgentState()
        self.human_feedback: List[str] = []
        self.agent_history: List[Dict[str, Any]] = []
        
    async def start(self) -> bool:
        """Start the agent execution"""
        try:
            if self.state.status == AgentStatus.RUNNING:
                return False
                
            self.state.status = AgentStatus.RUNNING
            self.state.current_step = 0
            self.state.start_time = time.time()
            self.state.last_error = None
            
            # Simulate agent execution
            await self._run_agent_steps()
            return True
            
        except Exception as e:
            self.state.status = AgentStatus.ERROR
            self.state.last_error = str(e)
            return False
    
    async def stop(self) -> bool:
        """Stop the agent execution"""
        try:
            if self.state.status != AgentStatus.RUNNING:
                return False
                
            self.state.status = AgentStatus.STOPPED
            return True
            
        except Exception as e:
            self.state.last_error = str(e)
            return False
    
    async def reset(self) -> bool:
        """Reset the agent to initial state"""
        try:
            self.state = AgentState()
            self.human_feedback.clear()
            self.agent_history.clear()
            return True
            
        except Exception as e:
            self.state.last_error = str(e)
            return False
    
    async def _run_agent_steps(self):
        """Simulate agent execution steps"""
        for step in range(self.config.num_steps):
            if self.state.status != AgentStatus.RUNNING:
                break
                
            self.state.current_step = step + 1
            self.state.memory_usage = 50 + (step * 5)  # Simulate memory usage
            
            # Simulate agent thinking and response generation
            await asyncio.sleep(0.1)  # Simulate processing time
            
            # Generate output based on system message
            response = f"Step {step + 1}: Processing request based on '{self.config.system_message}'"
            self.state.output = response
            
            # Add to history
            self.agent_history.append({
                "step": step + 1,
                "output": response,
                "timestamp": time.time(),
                "memory_usage": self.state.memory_usage
            })
    
    def add_human_feedback(self, feedback: str):
        """Add human feedback to the agent"""
        self.human_feedback.append({
            "feedback": feedback,
            "timestamp": time.time()
        })
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "status": self.state.status.value,
            "current_step": self.state.current_step,
            "total_steps": self.config.num_steps,
            "memory_usage": self.state.memory_usage,
            "output": self.state.output,
            "last_error": self.state.last_error,
            "uptime": time.time() - self.state.start_time if self.state.start_time else 0
        }
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration"""
        return asdict(self.config)
    
    def update_config(self, **kwargs):
        """Update agent configuration"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get agent execution history"""
        return self.agent_history.copy()
    
    def get_feedback(self) -> List[Dict[str, Any]]:
        """Get human feedback history"""
        return self.human_feedback.copy()

class HumanoidAgentManager:
    def __init__(self):
        self.agents: Dict[str, HumanoidAgent] = {}
    
    def create_agent(self, agent_id: str, config: Optional[AgentConfig] = None) -> HumanoidAgent:
        """Create a new agent"""
        agent = HumanoidAgent(config)
        self.agents[agent_id] = agent
        return agent
    
    def get_agent(self, agent_id: str) -> Optional[HumanoidAgent]:
        """Get agent by ID"""
        return self.agents.get(agent_id)
    
    def list_agents(self) -> List[str]:
        """List all agent IDs"""
        return list(self.agents.keys())
    
    def remove_agent(self, agent_id: str) -> bool:
        """Remove an agent"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            return True
        return False