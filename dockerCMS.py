#Written By Dimiter Dinkov
#Student number: C15334276  
#Cloud Computing Assignment


#importing all packages needed
from flask import Flask, Response, render_template, request
import json
from subprocess import Popen, PIPE
import os
from tempfile import mkdtemp
from werkzeug import secure_filename

app = Flask(__name__)

#This route was already completed
@app.route("/")
def index():
    return """
Available API endpoints:

GET /containers                     List all containers
GET /containers?state=running      List running containers (only)
GET /containers/<id>                Inspect a specific container
GET /containers/<id>/logs           Dump specific container logs
GET /images                         List all images


POST /images                        Create a new image
POST /containers                    Create a new container

PATCH /containers/<id>              Change a container's state
PATCH /images/<id>                  Change a specific image's attributes

DELETE /containers/<id>             Delete a specific container
DELETE /containers                  Delete all containers (including running)
DELETE /images/<id>                 Delete a specific image
DELETE /images                      Delete all images

"""
#This route was also completed
@app.route('/containers', methods=['GET'])
def containers_index():
    """
    List all containers
 
    curl -s -X GET -H 'Accept: application/json' http://localhost:8080/containers | python -mjson.tool
    curl -s -X GET -H 'Accept: application/json' http://localhost:8080/containers?state=running | python -mjson.tool

    """
    if request.args.get('state') == 'running': 
        output = docker('ps')
        resp = json.dumps(docker_ps_to_array(output))
         
    else:
        output = docker('ps', '-a')
        resp = json.dumps(docker_ps_to_array(output))


    return Response(response=resp, mimetype="application/json")

#
@app.route('/images', methods=['GET'])
def images_index():
    """
    List all images 
    
    Complete the code below generating a valid response. 
 
 """
    #Get the result from the command docker images and assign it to output
    output = docker('images')
    #parse output to an array and assign it to resp
    resp = json.dumps(docker_ps_to_array(output))
    #return the response aka. list of all images
    return Response(response=resp, mimetype="application/json")

#inspecting a container with specific id
#pass in the id from the route
@app.route('/containers/<id>', methods=['GET'])
def containers_show(id):
    """
    Inspect specific container

    """
    #assign the result from the command docker inspect id
    #where id is passed in from the browser
    output = docker('inspect',id)
    #assign the output to resp
    resp = output
    #return resp       
    return Response(response=resp, mimetype="application/json")

#get the logs for a specific container
#pass in the id from route
@app.route('/containers/<id>/logs', methods=['GET'])
def containers_log(id):
    """
    Dump specific container logs

    """
    #assign the result from the commad docker logs id(where id is passed in from browser) to output
    output = docker('logs',id)
    #assign output to resp
    resp = output
    #return a response
    return Response(response=resp, mimetype="application/json")

#delete a specific image by passing in an id
#id is passed in by http 
@app.route('/images/<id>', methods=['DELETE'])
def images_remove(id):
    """
    Delete a specific image
 '   """
    #run the docker command for removing and image 
    docker ('rmi', id)
    #resp = the id of the deleted image
    resp = '{"id": "%s"}' % id
    return Response(response=resp, mimetype="application/json")

#delete a specific container by passing in an id
#id is passed in by http
@app.route('/containers/<id>', methods=['DELETE'])
def containers_remove(id):
    """
    Delete a specific container - must be already stopped/killed

    """
    #run command to stop the container
    docker ('stop',id)
    #run docker command to remove the container
    docker ('rm',id)
    #resp = id of the container that was deleted
    resp = '{"id":%s"}' % id
    
    return Response(response=resp, mimetype="application/json")

#route to delete all containers
@app.route('/containers', methods=['DELETE'])
def containers_remove_all():
    """
    Force remove all containers - dangrous!

    """

    #assign the result of docker ps -a to a variable
    all_containers = docker('ps','-a')
    #turn this variable into array and assign it to containers
    containers = docker_ps_to_array(all_containers)
    
    #go in a for loop and for every index in the array of containers stop 
    #the container with the corresponding id and remove it
    for container in containers:
        docker('stop',container["id"])
    for container in containers:
        docker('rm',container["id"])

    resp = 'Containers deleted'
    #write a response when done
    return Response(response=resp, mimetype="application/json")

#deleting all images
@app.route('/images', methods=['DELETE'])
def images_remove_all():
    """
    Force remove all images - dangrous!

    """
    #get the result of docker images and assign it to a variable
    all_images = docker('images')
    #turn this variable to an array and assign it to images
    images = docker_ps_to_array(all_images)
    #in a for loop delete every image 
    for image in images:
        docker('rmi',image['id'],'-f')

    resp = 'Images deleted'
    #return a response when done
    return Response(response=resp, mimetype="application/json")


@app.route('/containers', methods=['POST'])
def containers_create():
    """
    Create container (from existing image using id or name)

    curl -X POST -H 'Content-Type: application/json' http://localhost:8080/containers -d '{"image": "my-app"}'
    curl -X POST -H 'Content-Type: application/json' http://localhost:8080/containers -d '{"image": "b14752a6590e"}'
    curl -X POST -H 'Content-Type: application/json' http://localhost:8080/containers -d '{"image": "b14752a6590e","publish":"8081:22"}'

    """
    body = request.get_json(force=True)
    image = body['image']
    args = ('run', '-d')
    id = docker(*(args + (image,)))[0:12]
    return Response(response='{"id": "%s"}' % id, mimetype="application/json")


@app.route('/images', methods=['POST'])
def images_create():
    """
    Create image (from uploaded Dockerfile)

    curl -H 'Accept: application/json' -F file=@Dockerfile http://localhost:8080/images -d '{"name": "newImage"}

    """
    dockerfile = request.files['file']
    name = body['name']
    args = ('build','-t')
    id = docker('build','-t',name,'.')
    resp = '{"id" : "%s"}' % id
    return Response(response=resp, mimetype="application/json")




@app.route('/containers/<id>', methods=['PATCH'])
def containers_update(id):
    """
    Update container attributes (support: state=running|stopped)

    curl -X PATCH -H 'Content-Type: application/json' http://localhost:8080/containers/b6cd8ea512c8 -d '{"state": "running"}'
    curl -X PATCH -H 'Content-Type: application/json' http://localhost:8080/containers/b6cd8ea512c8 -d '{"state": "stopped"}'

    """
    body = request.get_json(force=True)
    try:
        state = body['state']
        if state == 'running':
            docker('restart', id)
    except:
        pass

    resp = '{"id": "%s"}' % id
    return Response(response=resp, mimetype="application/json")

@app.route('/images/<id>', methods=['PATCH'])
def images_update(id):
    """
    Update image attributes (support: name[:tag])  tag name should be lowercase only

    curl -s -X PATCH -H 'Content-Type: application/json' http://localhost:8080/images/7f2619ed1768 -d '{"tag": "test:1.0"}'
    """
    body = request.get_json(force=true)
    resp = docker('tag',id,body['tag'])
    return Response(response=resp, mimetype="application/json")


def docker(*args):
    cmd = ['docker']
    for sub in args:
        cmd.append(sub)
    process = Popen(cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    if stderr.startswith('Error'):
        print ('...') 
        #print 'Error: {0} -> {1}'.format(' '.join(cmd), stderr)
    return stderr + stdout

# 
# Docker output parsing helpers
#

#
# Parses the output of a Docker PS command to a python List
# 
def docker_ps_to_array(output):
    all = []
    for c in [line.split() for line in output.splitlines()[1:]]:
        each = {}
        each['id'] = c[0]
        each['image'] = c[1]
        each['name'] = c[-1]
        each['ports'] = c[-2]
        all.append(each)
    return all

#
# Parses the output of a Docker logs command to a python Dictionary
# (Key Value Pair object)
def docker_logs_to_object(id, output):
    logs = {}
    logs['id'] = id
    all = []
    for line in output.splitlines():
        all.append(line)
    logs['logs'] = all
    return logs

#
# Parses the output of a Docker image command to a python List
# 
def docker_images_to_array(output):
    all = []
    for c in [line.split() for line in output.splitlines()[1:]]:
        each = {}
        each['id'] = c[2]
        each['tag'] = c[1]
        each['name'] = c[0]
        all.append(each)
    return all

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=8080, debug=True)
