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
                    echo "===== Docker Version ====="
                    docker --version

                    echo "===== Kubernetes Client ====="
                    kubectl version --client

                    echo "===== Minikube Status ====="
                    kubectl get nodes
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    echo "Building Docker image..."

                    docker build \
                    -t ${IMAGE_NAME}:${IMAGE_TAG} \
                    -t ${IMAGE_NAME}:latest .
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
                    echo "Pushing image ${IMAGE_TAG}"

                    docker push ${IMAGE_NAME}:${IMAGE_TAG}
                    docker push ${IMAGE_NAME}:latest
                '''
            }
        }

        stage('Deploy To Kubernetes') {
            steps {
                sh '''
                    export KUBECONFIG=/var/lib/jenkins/.kube/config

                    echo "Deploying application..."

                    kubectl apply --validate=false -f deployment.yaml
                    kubectl apply --validate=false -f service.yaml
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                sh '''
                    export KUBECONFIG=/var/lib/jenkins/.kube/config

                    echo "===== Deployments ====="
                    kubectl get deployments

                    echo "===== Pods ====="
                    kubectl get pods

                    echo "===== Services ====="
                    kubectl get svc

                    echo "===== Rollout Status ====="
                    kubectl rollout status deployment/house-price-api --timeout=300s
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
