#!/bin/bash

curl -k -X GET "http://localhost:8080/api/permission/roles" -H "Content-Type: application/json" -H "Authorization: Bearer $token"