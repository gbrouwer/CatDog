1. Project Overview
Project Name: CatDog Project​
turnkeylinux.org
+1
Reddit
+1

Objective: Develop a distributed system where multiple devices (e.g., Raspberry Pi and PC) collaborate to perform tasks, with each device running an agent that communicates and coordinates with others.​

Key Components:

Agents: Python scripts running on each device, responsible for executing tasks and communicating with other agents.​

Coordinator: A central entity (possibly one of the agents) that initiates and manages tasks across devices.​

Communication: Utilizes SSH and tmux to remotely execute scripts and manage sessions on different devices.​

2. Philosophy Behind the Project
The CatDog Project is built upon the following principles:

Modularity: Each component (agent) operates independently, allowing for easy scalability and maintenance.​

Decentralization: While there may be a coordinator, each agent has the capability to function autonomously, enhancing robustness.​

Automation: Tasks such as launching agents on remote devices are automated using scripts and tools like tmux and SSH.​

Simplicity: Avoid unnecessary complexity by leveraging existing tools and straightforward Python scripts.​

3. Architectural Implementation
a. System Architecture:

Devices: Multiple devices (e.g., Raspberry Pi, PC) connected over a network.​

Agents: Python scripts (agent.py) running on each device.​

Coordinator: A designated agent responsible for initiating tasks across devices.​

b. Process Flow:

Initialization: The coordinator reads a configuration file (catdog_test.yaml) containing information about all devices.​

Agent Launch: For each device (excluding itself), the coordinator uses SSH to remotely execute a command that starts agent.py within a new tmux session.​

Task Execution: Each agent performs its designated tasks and communicates results back to the coordinator or other agents as needed.​

c. Classes and Functions:

AgentLauncher: A class responsible for reading the configuration file and launching agents on remote devices.​

launch_remote_agents(): Iterates through the list of devices and uses SSH to start agent.py in a new tmux session on each.​

4. Detailed Overview of the Existing Codebase
a. Configuration File:

catdog_test.yaml: Contains details about each device, including IP address, SSH user, path to agent.py, and path to the configuration file.​

b. Python Scripts:

agent.py: The main script that runs on each device. It reads the configuration file and performs tasks as specified.​

Key Functions:

main(): Entry point of the script. Parses arguments and initiates tasks.

perform_tasks(): Carries out the specific tasks assigned to the agent.

launcher.py: Script responsible for initiating agents on remote devices.​

Key Functions:

launch_remote_agents(): Uses SSH and tmux to start agent.py on each remote device.

c. Supporting Files:

.bashrc: Contains configurations to automatically activate virtual environments upon SSH login (though this behavior has been modified as per recent changes).​

5. Current Project Status and Issues
a. Progress:

The core functionality for launching agents on remote devices using SSH and tmux has been implemented.​

Configuration files are set up to define device-specific parameters.​

b. Current Issue:

Problem: When attempting to launch agent.py on the Raspberry Pi using the following command:​

bash
Copy
Edit
tmux new-session -d -s catdog_agent python /home/gbrouwer/CatDog/src/agent.py --config /home/gbrouwer/CatDog/catdog_test.yaml
No new tmux session is created, and the agent does not start.​

Investigations:

Virtual Environment: Initially, a virtual environment was used, but due to complications (e.g., the externally-managed-environment error), it was removed in favor of using the system Python.​

tmux Behavior: Running the command directly on the Raspberry Pi does not result in a new session, suggesting that the command may be failing silently.​

Potential Causes:

Script Termination: If agent.py executes and terminates quickly, the tmux session may close immediately after starting.​

Command Syntax: Improper command syntax or quoting may prevent tmux from executing the command correctly.​

Permissions: There may be permission issues preventing tmux from creating new sessions.​

Next Steps:

Add Delay: Modify agent.py to include a delay (e.g., input("Press Enter to exit...")) to keep the script running and observe tmux behavior.​

Check Logs: Examine system logs or tmux logs for any error messages related to session creation.​

Test Commands: Run simplified versions of the command to isolate the issue (e.g., tmux new-session -d -s test_session bash -c "echo 'Hello'; sleep 10").​

Verify Permissions: Ensure that the user has the necessary permissions to create tmux sessions.​

