#!/bin/bash
cd "$(dirname "$0")"

# Prompt the user for a directory
read -p "Enter the directory of your anaconda installation: " user_directory

# Check if the entered directory exists
if [ -d "$user_directory" ]; then
    # Append a path to the directory and use it in a source command
    source "$user_directory/etc/profile.d/conda.sh"
    #Backend dependencies (Python)
    conda create -n its python==3.11.4
    conda activate its
    echo "$PWD"
    pip install -r ~+/api/requirements.txt
else
    echo "The directory does not exist."
fi


#Frontend dependencies (Javascript/Angular)
#sudo apt-get install node
#sudo apt install npm
#sudo npm cache clean -fs
sudo apt-get install -y ca-certificates curl gnupg
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | sudo gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg
NODE_MAJOR=20
echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" | sudo tee /etc/apt/sources.list.d/nodesource.list
sudo apt-get update
sudo apt-get install nodejs -y
sudo npm install -g n
sudo n stable
sudo npm install -g @angular/cli

cd frontend/its_ui
sudo npm install

#Database dependencies (MongoDB)
wget https://repo.mongodb.org/apt/ubuntu/dists/jammy/mongodb-org/6.0/multiverse/binary-amd64/mongodb-org-server_6.0.8_amd64.deb
sudo dpkg -i mongodb-org-server_6.0.8_amd64.deb
rm mongodb-org-server_6.0.8_amd64.deb
sudo systemctl start mongod
systemctl enable mongod #Enable MongoDB service on every reboot!!!

#Install Mongo shell
read -p "Install MongoDB shell? [y/n] " install_shell

# Check the user's input
if [ "$install_shell" = "y" ] || [ "$install_shell" = "Y" ]; then
    echo "You chose to continue. Instaling Shell..."
    wget https://downloads.mongodb.com/compass/mongodb-mongosh_1.10.3_amd64.deb
    sudo dpkg -i mongodb-mongosh_1.10.3_amd64.deb
    rm mongodb-mongosh_1.10.3_amd64.deb
   #Run api/tasks/tasks_to_json and select database import to import tasks from a folder into the database
elif [ "$install_shell" = "n" ] || [ "$install_shell" = "N" ]; then
    echo "You chose to cancel. Exiting..."
    # Place your actions here that you want to perform if 'n' is selected.
else
    echo "Invalid input. Please select 'y' or 'n'."
fi


