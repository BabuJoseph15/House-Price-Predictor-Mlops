pipeline {
    agent any

    environment {
        IMAGE_NAME = "babujoseph5757/house-price-api"
        IMAGE_TAG = "${BUILD_NUMBER}"
        KUBECONFIG = "/var/lib/jenkins/.kube/config"
    }

    stages {

        stage('Checkout') {
            steps {
                echo "Checking out source code..."
                checkout scm
            }
        }

        stage('Verify Environment') {
            steps {
                sh '''
                    docker --version
                    kubectl version --client
                    kubectl get nodes
                '''
            }
        }

        stage('Run Unit Tests') {
            steps {
                sh '''
                    pip install -r requirements.txt
                    pytest tests/ -v
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build \
                    -t ${IMAGE_NAME}:${IMAGE_TAG} \
                    -t ${IMAGE_NAME}:latest .
                '''
            }
        }

        stage('Security Scan') {
            steps {
                sh '''
                    echo "Running Trivy Security Scan..."

                    trivy image \
                    --severity HIGH,CRITICAL \
                    --exit-code 1 \
                    --no-progress \
                    ${IMAGE_NAME}:${IMAGE_TAG}
                '''
            }
        }

        stage('Docker Login') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )
                ]) {
                    sh '''
                        echo "$DOCKER_PASS" | docker login \
                        -u "$DOCKER_USER" \
                        --password-stdin
                    '''
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                sh '''
                    docker push ${IMAGE_NAME}:${IMAGE_TAG}
                    docker push ${IMAGE_NAME}:latest
                '''
            }
        }

        stage('Deploy To Kubernetes') {
            steps {
                sh '''
                    export KUBECONFIG=/var/lib/jenkins/.kube/config

                    kubectl apply --validate=false -f deployment.yaml
                    kubectl apply --validate=false -f service.yaml
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                sh '''
                    export KUBECONFIG=/var/lib/jenkins/.kube/config

                    kubectl rollout status deployment/house-price-api --timeout=300s

                    kubectl get deployments
                    kubectl get pods
                    kubectl get svc
                '''
            }
        }
    }

    post {

        success {
            echo '✅ CI/CD Pipeline completed successfully!'
        }

        failure {
            echo '❌ Pipeline failed!'
        }

        always {
            sh 'docker image prune -f || true'
            cleanWs()
        }
    }
}
