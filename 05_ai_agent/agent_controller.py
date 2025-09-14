import asyncio
import json
from typing import Dict, Any, Optional
from humanoid_agent import HumanoidAgent, HumanoidAgentManager, AgentConfig

class AgentStatusMonitor:
    def __init__(self, agent_manager: HumanoidAgentManager):
        self.agent_manager = agent_manager
        self.monitoring = False
        self.update_interval = 0.5  # Update every 500ms
        
    async def start_monitoring(self, agent_id: str):
        """Start monitoring a specific agent"""
        self.monitoring = True
        while self.monitoring:
            agent = self.agent_manager.get_agent(agent_id)
            if agent:
                status = agent.get_status()
                self._update_status_display(status)
                
                if status["status"] in ["stopped", "error"]:
                    break
                    
            await asyncio.sleep(self.update_interval)
    
    def stop_monitoring(self):
        """Stop monitoring all agents"""
        self.monitoring = False
    
    def _update_status_display(self, status: Dict[str, Any]):
        """Update the status display (simulated)"""
        print(f"Status: {status['status'].upper()}")
        print(f"Step: {status['current_step']}/{status['total_steps']}")
        print(f"Memory: {status['memory_usage']:.1f}MB")
        print(f"Output: {status['output'][:100]}...")
        print("-" * 50)

class AgentController:
    def __init__(self, agent_manager: HumanoidAgentManager):
        self.agent_manager = agent_manager
        self.monitor = AgentStatusMonitor(agent_manager)
        
    async def start_agent(self, agent_id: str) -> bool:
        """Start an agent and begin monitoring"""
        agent = self.agent_manager.get_agent(agent_id)
        if not agent:
            return False
            
        success = await agent.start()
        if success:
            # Start monitoring in background
            asyncio.create_task(self.monitor.start_monitoring(agent_id))
        
        return success
    
    async def stop_agent(self, agent_id: str) -> bool:
        """Stop an agent"""
        agent = self.agent_manager.get_agent(agent_id)
        if not agent:
            return False
            
        return await agent.stop()
    
    async def reset_agent(self, agent_id: str) -> bool:
        """Reset an agent"""
        agent = self.agent_manager.get_agent(agent_id)
        if not agent:
            return False
            
        self.monitor.stop_monitoring()
        return await agent.reset()
    
    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get current agent status"""
        agent = self.agent_manager.get_agent(agent_id)
        if agent:
            return agent.get_status()
        return None
    
    def list_all_agents(self) -> Dict[str, Dict[str, Any]]:
        """List all agents with their status"""
        result = {}
        for agent_id in self.agent_manager.list_agents():
            agent = self.agent_manager.get_agent(agent_id)
            if agent:
                result[agent_id] = agent.get_status()
        return result

# Demo usage
async def demo_agent_controls():
    # Create agent manager and controller
    manager = HumanoidAgentManager()
    controller = AgentController(manager)
    
    # Create an agent with custom config
    config = AgentConfig(
        num_steps=5,
        model="gpt-4",
        temperature=0.7,
        system_message="You are a helpful weather assistant."
    )
    
    agent = manager.create_agent("weather_agent", config)
    
    # Start the agent
    print("Starting agent...")
    success = await controller.start_agent("weather_agent")
    print(f"Agent started: {success}")
    
    # Let it run for a bit
    await asyncio.sleep(2)
    
    # Check status
    status = controller.get_agent_status("weather_agent")
    print(f"Current status: {status}")
    
    # Stop the agent
    print("Stopping agent...")
    success = await controller.stop_agent("weather_agent")
    print(f"Agent stopped: {success}")
    
    # Reset the agent
    print("Resetting agent...")
    success = await controller.reset_agent("weather_agent")
    print(f"Agent reset: {success}")

if __name__ == "__main__":
    asyncio.run(demo_agent_controls())