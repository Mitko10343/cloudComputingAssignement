# cloudComputingAssignement


external ip of the vm : http://35.187.98.251/

Video Demo Link: https://www.youtube.com/watch?v=YIIKI9xFe4Y

Running the dockerCMS program:

Step 1:
type python dockerCMs.py

Step2:
Visit the externIp of the vm at port 8080 
eg: externalIp:8080/

Step3:
You can test the get methods of the program in the browser by visiting the routes.
eg: externalIP:8080/containers
    externalIP:8080/images
    
Step 4:
To test out any delete methods open a second window of the vm
and run the script in the first.
Then from the second window type in any of these curl commands]

//delete a specific container 
curl -s -X DELETE -H 'Accept: application/json' http://localhost:8080/containers/id| python -mjson.tool

//delete specific image
curl -s -X DELETE -H 'Accept: application/json' http://localhost:8080/images/id | python -mjson.tool

//delete all containers
curl -s -X DELETE -H 'Content-Type: application/json' http://localhost:8080/containers

//delete all images
curl -s -X DELETE -H 'Content-Type: application/json' http://localhost:8080/images

curl -s -X PATCH -H 'Content-Type: application/json' http://localhost:8080/images/id -d '{"tag": "tes
t:1.0"}'


(the id is the id of the containers or images you want to delete/ update)
