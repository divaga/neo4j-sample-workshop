# Neo4j Sample Workshop

## VM Preparation

We need to prepare virtual machine for our Neo4j. For list of supported platfom, you can see it on Neo4j Documentation here: https://neo4j.com/docs/operations-manual/current/installation/requirements/

We can use cloud based infrastructure for our virtual machine. For this workshop, we will use Amazon Lightsail but you can use any VPS instance.

1. Create VM with 2vCPU dan 2GiB RAM using Ubuntu
2. Configure server firewall to allow these following ports:
    - Port 22       : for SSH
    - Port 5000     : for our Flask application
    - Port 7474     : Neo4j Browser
    - Port 7687     : Neo4j

3. Access our VM using SSH and install Docker https://docs.docker.com/engine/install/ubuntu/

4. Create persistent path

```console
mkdir neo4j
cd neo4j
mkdir data
mkdir logs
```

5. Set folder permission to neo4j user

```console
sudo useradd neo4j -p your-strong-password
sudo usermod -a -G neo4j neo4j
sudo chown neo4j:neo4j /path-to-your-data/neo4j/data
sudo chown neo4j:neo4j /path-to-your-data/logs
```

6. Run Neo4j Enterprise Docker images from DockerHub

```console
sudo docker run -d \
    --restart always \
    --publish=7474:7474 --publish=7687:7687 \
    --env NEO4J_AUTH=neo4j/your-neo4j-password \
    --env NEO4J_ACCEPT_LICENSE_AGREEMENT=yes \
    --volume=/path/to/your/data:/data \
    --volume=/path/to/your/logs:/logs \
    neo4j:5.8.0-enterprise
```
7. Using your local browser, test Neo4j Browser by accessing http://your-server-address:7474, and setup your database credentials

![images](assets/connect.png)

8. You will get into Neo4j Browser

![images](assets/start.png)

## Prepare dataset

We will use sample dataset from here: https://gist.github.com/maruthiprithivi/10b456c74ba99a35a52caaffafb9d3dc. Please download those 4 files into your local drive.

We will use following model for our database:

![images](assets/sng.png)

You can download JSON model definition for Arrows.app [here](assets/SocialNetworkGraphModel.json)

## Create and Deploy Sample Application

1. Prepare server Python libraries

```console
pip install flask
pip install neo4j
pip install flask-wtf wtforms
pip install flask_login
```

2. We provide sample application here: https://github.com/divaga/neo4j-sample-workshop/tree/main/apps, you can download and copy it into your virtual machine. Modify app.py for Neo4j address, password and also application credentials.

3. Start this application by execute this command:

```console
flask run --host=0.0.0.0
```

4. After login, you can see our sample application running.

![images](assets/apps.png)

5. You can upload csv files to automatically create nodes and relationship or you can manually create nodes and relationship.

## Exploratory Cypher queries

You can try following exploratory Cypher queries using Neo4j Browser
