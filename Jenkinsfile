pipeline {
    agent any

    environment {
        IMAGE_NAME = "BabuJoseph15/house-price-api"
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
                    echo "===== Python ====="
                    python3 --version

                    echo "===== Docker ====="
                    docker --version

                    echo "===== Kubectl ====="
                    kubectl version --client

                    echo "===== Kubernetes ====="
                    kubectl get nodes
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    python3 -m pip install --upgrade pip

                    python3 -m pip install -r requirements.txt
                '''
            }
        }

        stage('Run Unit Tests') {
            steps {
                sh '''
                    if [ -d tests ]; then
                        python3 -m pytest tests/ -v
                    else
                        echo "No tests directory found - skipping"
                    fi
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
                    if command -v trivy >/dev/null 2>&1; then
                        trivy image \
                        --severity HIGH,CRITICAL \
                        --no-progress \
                        ${IMAGE_NAME}:${IMAGE_TAG} \
                        > trivy-report.txt

                        cat trivy-report.txt
                    else
                        echo "Trivy not installed. Skipping security scan."
                    fi
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
