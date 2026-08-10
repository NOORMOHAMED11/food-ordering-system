pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                echo 'Checking out Food Ordering System...'
                checkout scm
            }
        }

        stage('Build') {
            steps {
                echo 'Building application...'
            }
        }

        stage('Docker Build') {
            steps {
                echo 'Building Docker image...'
                sh 'docker build -t noormohamed11/food-ordering-backend:latest ./backend'
            }
        }

        stage('Docker Test') {
            steps {
                echo 'Checking Docker image...'
                sh 'docker images noormohamed11/food-ordering-backend'
            }
        }

        stage('Docker Hub Push') {
            steps {
                echo 'Pushing image to Docker Hub...'

                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub',
                        usernameVariable: 'DOCKER_USERNAME',
                        passwordVariable: 'DOCKER_PASSWORD'
                    )
                ]) {
                    sh '''
                        echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
                        docker push noormohamed11/food-ordering-backend:latest
                        docker logout
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'CI/CD pipeline completed successfully!'
        }

        failure {
            echo 'CI/CD pipeline failed!'
        }
    }
}