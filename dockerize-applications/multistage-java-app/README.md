# Multi-Stage Java Application

This is a simple Spring Boot application that demonstrates multi-stage Docker builds.

## Project Structure
```
multistage-java-app/
├── src/
│   └── main/
│       └── java/
│           └── com/
│               └── example/
│                   └── demo/
│                       ├── DemoApplication.java
│                       └── controller/
│                           └── HelloController.java
├── pom.xml
├── Dockerfile
└── README.md
```

## Building and Running

### Using Docker
1. Build the Docker image:
```bash
docker build -t multistage-java-app .
```

2. Run the container:
```bash
docker run -p 8080:8080 multistage-java-app
```

3. Access the application:
Open your browser and navigate to `http://localhost:8080/hello`

### Using Maven
1. Build the application:
```bash
mvn clean package
```

2. Run the application:
```bash
java -jar target/demo-0.0.1-SNAPSHOT.jar
```

## Features
- Simple REST endpoint at `/hello`
- Multi-stage Docker build for optimized image size
- Uses Java 17 and Spring Boot 3.2.3