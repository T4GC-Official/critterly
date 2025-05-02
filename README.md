## Critterly: Where citizen curiosity meets the wild.

![Screenshot from 2025-05-02 17-46-57](https://github.com/user-attachments/assets/c736d9fd-00da-455c-a2f9-5e8ce0019d46)


See demo [video](https://drive.google.com/file/d/1x_lQx6SYUPJDirE5IBbWgUlYXHlwCHfq/view?usp=sharing) for overview. 

__Disclaimer__: This repo only contains a proof-of-concept. A significant amount of community works needs to be done to make it production ready. Specifically, most of the assets in the video above were processed offline, not through APIs or a database, but through files that are all checked into this repo. For example in order to generate the podcast mp3 the developers of this repo has to run scripts by hand. So the remaing work is to API-ify these scripts. For more documentation around this, see the [docs](./docs) folder.

## Running critterly

via docker  (development)
```
$ cd app
$ docker run -it -v `pwd`:/app -p 8080:8080 cws_frontend
```

via docker (release)
```
$ docker run -d -p 8080:8080 bprashanth/cws_frontend:0.1
```

via npm 
```
$ npm install 
$ npm run serve
```
