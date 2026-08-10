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
    }

    post {
        success {
            echo 'CI pipeline completed successfully!'
        }

        failure {
            echo 'CI pipeline failed!'
        }
    }
}