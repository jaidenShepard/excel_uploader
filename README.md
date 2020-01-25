# Excel Uploader

## Run Application
From inside the project folder, run `docker-compose up -d`
The app will be exposed on your `localhost:8000`
Api docs can be found at `localhost:8000/docs`

## Design considerations
The structure of the project was based on the structure of my recent work projects,
more out of habit than anything. Since FastAPI is a 'batteries included' framework, I stuck with their included tools, which were a pleasure to use.
One improvement I would make would be to validate the file size before it makes it to the makes it to the endpoint. As it stands, because it's using a SpooledTemporaryFile, python will intelligently overflow large files to the file system, so it wouldn't eat up all the ram, though I suspect it could maybe be an attack vector.