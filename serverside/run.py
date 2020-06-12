from server import create_app # import function that returns an applicaiton

app = create_app() # gets it 

if __name__ == '__main__':
    app.run(port = 8080) # runs the application