"""
Multi-Agent System: Producer-Consumer Task Management
A complete implementation of two agents collaborating through message passing
"""

import threading
import queue
import time
import random
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from typing import Optional
import logging

# Configure logging for better visibility
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# ============================================================================
# STEP 1: Define Task Structure (Messages between agents)
# ============================================================================

class TaskType(Enum):
    """Types of tasks that can be processed"""
    DATA_PROCESSING = "data_processing"
    EMAIL_SENDING = "email_sending"
    REPORT_GENERATION = "report_generation"
    DATABASE_UPDATE = "database_update"
    POISON_PILL = "poison_pill"  # Special task to signal shutdown

@dataclass
class Task:
    """
    Task object that agents pass between each other
    This is our "message" format
    """
    task_id: int
    task_type: TaskType
    priority: int  # 1 (low) to 5 (high)
    data: dict
    created_at: datetime
    
    def __repr__(self):
        return f"Task({self.task_id}, {self.task_type.value}, P{self.priority})"


# ============================================================================
# STEP 2: Define Base Agent Class
# ============================================================================

class Agent(threading.Thread):
    """
    Base Agent class - all agents inherit from this
    Uses threading to run independently
    """
    def __init__(self, name: str):
        super().__init__()
        self.name = name
        self.logger = logging.getLogger(self.name)
        self.running = False
        self.daemon = True  # Thread dies when main program exits
        
    def start_agent(self):
        """Start the agent's operation"""
        self.running = True
        self.start()
        self.logger.info(f"🚀 {self.name} started")
        
    def stop_agent(self):
        """Stop the agent gracefully"""
        self.running = False
        self.logger.info(f"🛑 {self.name} stopping")


# ============================================================================
# STEP 3: Implement Producer Agent
# ============================================================================

class ProducerAgent(Agent):
    """
    Producer Agent: Creates tasks and puts them in the queue
    Simulates a user or system generating work
    """
    def __init__(self, name: str, task_queue: queue.Queue, num_tasks: int = 10):
        super().__init__(name)
        self.task_queue = task_queue
        self.num_tasks = num_tasks
        self.tasks_created = 0
        
    def generate_task(self) -> Task:
        """Create a new task with random properties"""
        self.tasks_created += 1
        
        task_types = [
            TaskType.DATA_PROCESSING,
            TaskType.EMAIL_SENDING,
            TaskType.REPORT_GENERATION,
            TaskType.DATABASE_UPDATE
        ]
        
        task = Task(
            task_id=self.tasks_created,
            task_type=random.choice(task_types),
            priority=random.randint(1, 5),
            data={
                "payload": f"Data for task {self.tasks_created}",
                "user_id": random.randint(1000, 9999)
            },
            created_at=datetime.now()
        )
        
        return task
    
    def run(self):
        """
        Main execution loop for Producer Agent
        This runs in a separate thread
        """
        self.logger.info(f"📝 Starting to produce {self.num_tasks} tasks")
        
        for i in range(self.num_tasks):
            if not self.running:
                break
                
            # Generate a task
            task = self.generate_task()
            
            # Put task in queue (this is the "communication" step)
            self.task_queue.put(task)
            self.logger.info(f"✅ Produced: {task}")
            
            # Simulate variable production rate
            time.sleep(random.uniform(0.5, 2.0))
        
        # Send poison pill to signal consumer to stop
        self.task_queue.put(Task(
            task_id=-1,
            task_type=TaskType.POISON_PILL,
            priority=10,
            data={},
            created_at=datetime.now()
        ))
        
        self.logger.info(f"✨ Finished producing. Total tasks: {self.tasks_created}")


# ============================================================================
# STEP 4: Implement Consumer Agent
# ============================================================================

class ConsumerAgent(Agent):
    """
    Consumer Agent: Takes tasks from queue and processes them
    Simulates a worker completing tasks
    """
    def __init__(self, name: str, task_queue: queue.Queue):
        super().__init__(name)
        self.task_queue = task_queue
        self.tasks_processed = 0
        self.processing_times = []
        
    def process_task(self, task: Task) -> bool:
        """
        Process a single task
        Returns True if successful, False otherwise
        """
        self.logger.info(f"🔨 Processing: {task}")
        
        # Simulate processing time based on task type and priority
        base_time = {
            TaskType.DATA_PROCESSING: 2.0,
            TaskType.EMAIL_SENDING: 0.5,
            TaskType.REPORT_GENERATION: 3.0,
            TaskType.DATABASE_UPDATE: 1.5,
        }.get(task.task_type, 1.0)
        
        # Higher priority tasks process faster
        processing_time = base_time * (6 - task.priority) / 5
        
        time.sleep(processing_time)
        
        # Simulate occasional failures (10% chance)
        if random.random() < 0.1:
            self.logger.warning(f"❌ Failed to process: {task}")
            return False
        
        self.tasks_processed += 1
        self.processing_times.append(processing_time)
        self.logger.info(f"✅ Completed: {task} (took {processing_time:.2f}s)")
        return True
    
    def run(self):
        """
        Main execution loop for Consumer Agent
        Continuously checks queue for new tasks
        """
        self.logger.info("👂 Listening for tasks...")
        
        while self.running:
            try:
                # Wait for a task (timeout after 1 second to check if still running)
                task = self.task_queue.get(timeout=1.0)
                
                # Check for poison pill (shutdown signal)
                if task.task_type == TaskType.POISON_PILL:
                    self.logger.info("💊 Received poison pill - shutting down")
                    break
                
                # Process the task
                success = self.process_task(task)
                
                # Mark task as done in queue
                self.task_queue.task_done()
                
                if not success:
                    # In a real system, you might retry or send to error queue
                    self.logger.info(f"📤 Task {task.task_id} sent to error queue")
                    
            except queue.Empty:
                # No tasks available, continue waiting
                continue
            except Exception as e:
                self.logger.error(f"💥 Error processing task: {e}")
        
        # Calculate statistics
        if self.processing_times:
            avg_time = sum(self.processing_times) / len(self.processing_times)
            self.logger.info(f"📊 Processed {self.tasks_processed} tasks")
            self.logger.info(f"📊 Average processing time: {avg_time:.2f}s")


# ============================================================================
# STEP 5: System Monitor (Optional but helpful)
# ============================================================================

class SystemMonitor(Agent):
    """
    Monitor Agent: Tracks system health and queue status
    This is a third agent that observes the others
    """
    def __init__(self, name: str, task_queue: queue.Queue, 
                 producer: ProducerAgent, consumer: ConsumerAgent):
        super().__init__(name)
        self.task_queue = task_queue
        self.producer = producer
        self.consumer = consumer
        
    def run(self):
        """Monitor system status every 3 seconds"""
        self.logger.info("📡 System monitoring started")
        
        while self.running:
            if not self.producer.is_alive() and self.task_queue.empty():
                # Both producer finished and queue empty - time to shut down
                self.logger.info("🏁 All tasks completed - system shutting down")
                self.consumer.stop_agent()
                break
            
            # Log current status
            queue_size = self.task_queue.qsize()
            self.logger.info(
                f"📊 Status - Queue: {queue_size} | "
                f"Produced: {self.producer.tasks_created} | "
                f"Processed: {self.consumer.tasks_processed}"
            )
            
            time.sleep(3)


# ============================================================================
# STEP 6: Main Orchestration
# ============================================================================

def run_multi_agent_system(num_tasks: int = 10):
    """
    Main function to set up and run the multi-agent system
    
    Args:
        num_tasks: Number of tasks for producer to create
    """
    print("\n" + "="*70)
    print("🤖 MULTI-AGENT SYSTEM: Producer-Consumer Task Management")
    print("="*70 + "\n")
    
    # Create shared communication channel (queue)
    task_queue = queue.Queue(maxsize=5)  # Buffer of 5 tasks
    
    # Create agents
    producer = ProducerAgent("Producer-1", task_queue, num_tasks)
    consumer = ConsumerAgent("Consumer-1", task_queue)
    monitor = SystemMonitor("Monitor", task_queue, producer, consumer)
    
    # Start all agents
    print("🚀 Starting agents...\n")
    producer.start_agent()
    time.sleep(0.5)  # Small delay to let producer start first
    consumer.start_agent()
    time.sleep(0.5)
    monitor.start_agent()

    # Wait for all agents to finish
    try:
        producer.join()  # Wait for producer to finish
        consumer.join()  # Wait for consumer to finish
        monitor.stop_agent()
        monitor.join()   # Wait for monitor to finish
        
        print("\n" + "="*70)
        print("✅ MULTI-AGENT SYSTEM COMPLETED SUCCESSFULLY")
        print("="*70)
        print(f"\n📊 Final Statistics:")
        print(f"   • Tasks Created: {producer.tasks_created}")
        print(f"   • Tasks Processed: {consumer.tasks_processed}")
        print(f"   • Queue Status: {'Empty ✓' if task_queue.empty() else 'Has items'}")
        print()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  System interrupted by user")
        producer.stop_agent()
        consumer.stop_agent()
        monitor.stop_agent()


# ============================================================================
# STEP 7: Run the System
# ============================================================================

if __name__ == "__main__":
    # Run with 15 tasks
    run_multi_agent_system(num_tasks=15)
    
    print("\n💡 TIP: Try modifying these parameters:")
    print("   • Change num_tasks to create more/fewer tasks")
    print("   • Adjust queue maxsize to see buffer effects")
    print("   • Modify processing times in process_task()")
    print("   • Add more consumer agents for parallel processing")
