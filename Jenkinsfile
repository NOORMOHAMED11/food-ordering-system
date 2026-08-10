stage('Docker Build') {
    steps {
        echo 'Building Docker image...'
        sh 'docker build -t noormohamed11/food-ordering-backend:latest ./backend'
    }
}

stage('Docker Test') {
    steps {
        echo 'Docker image created successfully!'
        sh 'docker images noormohamed11/food-ordering-backend'
    }
}