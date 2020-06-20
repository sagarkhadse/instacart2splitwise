# Instacart to Splitwise export
Exports the order details from instacart to splitwise.
1. Logs into the Instacart account and extracts the order details for the latest order. 
2. Logs into the Splitwise account and creates a new itemized expense in a group using the order details. 

# Config.json format
    {
        "instacart" : {
            "username" : "",    --> Instacart email
            "password" : ""     --> Instacart password
        },
        "splitwise" : {
            "username" : "",    --> Splitwise email
            "password" : "",    --> Splitwise password
            "group" : ""        --> Group no. [Check the url of the group to get the number]
        }
    }
