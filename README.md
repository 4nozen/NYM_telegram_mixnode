### NYM_telegram_mixnode
## telegram mixnode monitor<br>
![image](https://github.com/user-attachments/assets/4b4a197a-220e-4c6a-a836-5617cb9a9048)
![image](https://github.com/user-attachments/assets/e1301fa5-b5d2-481a-85bb-90f4b6f8b5e3)

## You can try it here https://t.me/nym_mixnode_monitor_bot


## self installation
1. sudo apt install python3 python-dotenv: This command installs Python 3 and the python-dotenv package on a Linux system using the APT package manager. python-dotenv is used for loading environment variables from a .env file.<br>
`sudo apt install python3 python-dotenv`

2. git clone https://github.com/4nozen/NYM_telegram_mixnode.git: This command clones the repository from GitHub, downloading the project's files to your local machine.<br>
`git clone https://github.com/4nozen/NYM_telegram_mixnode.git`

3. cd NYM_telegram_mixnode: This command changes the current directory to the cloned project folder.<br>
`cd NYM_telegram_mixnode`

4. python -m venv venv: This command creates a new virtual environment named "venv" in the project directory. A virtual environment isolates the project's dependencies from the global Python installation.<br>
`python -m venv venv`

5. source venv/bin/activate: This command activates the virtual environment, allowing you to install packages and run scripts using the isolated environment.<br>
`source venv/bin/activate`

6. pip install -r requirements.txt: This command installs all the Python packages listed in the requirements.txt file, which are necessary for the project to run.<br>
`pip install -r requirements.txt`

7. nano config.py: This command opens the config.py file in the Nano text editor, allowing you to edit configuration settings for the project.<br>
   insert the api of your telegram bot<br>
`nano config.py`

9. python3 main.py: This command runs the main Python script of the project, which likely starts the monitoring functionality.<br>
`python3 main.py`
