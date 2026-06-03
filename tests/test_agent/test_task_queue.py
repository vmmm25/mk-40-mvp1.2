import pytest
import time
from agent.task_queue import TaskQueue, TaskPriority, TaskStatus

def test_task_queue_submit_and_cancel():
    queue = TaskQueue(max_concurrent=1)
    
    # We won't start the queue so the tasks remain pending
    task_id1 = queue.submit("Test Goal 1", priority=TaskPriority.NORMAL)
    task_id2 = queue.submit("Test Goal 2", priority=TaskPriority.HIGH)
    
    assert queue.pending_count() == 2
    
    # High priority task should be first in the queue
    # The queue uses TaskPriority values (Enum): LOW=3, NORMAL=2, HIGH=1
    assert queue._queue[0].task_id == task_id2
    assert queue._queue[1].task_id == task_id1
    
    # Cancel task
    assert queue.cancel(task_id1) == True
    status = queue.get_status(task_id1)
    assert status["status"] == TaskStatus.CANCELLED.value

def test_get_status():
    queue = TaskQueue(max_concurrent=1)
    task_id = queue.submit("Test Goal", priority=TaskPriority.NORMAL)
    
    status = queue.get_status(task_id)
    assert status is not None
    assert status["goal"] == "Test Goal"
    assert status["status"] == TaskStatus.PENDING.value

def test_get_all_statuses():
    queue = TaskQueue(max_concurrent=1)
    queue.submit("Task A")
    queue.submit("Task B")
    
    statuses = queue.get_all_statuses()
    assert len(statuses) == 2
