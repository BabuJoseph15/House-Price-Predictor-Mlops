pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "babujoseph5757/house-price-api"
        KUBECONFIG = "/var/lib/jenkins/.kube/config"
    }

    options {
        timestamps()
        skipDefaultCheckout(true)
    }

    stages {

        stage('Checkout Code') {
            steps {
                git branch: 'master',
                    url: 'https://github.com/BabuJoseph15/House-Price-Predictor-Mlops.git'
            }
        }

        stage('Verify Files') {
            steps {
                sh '''
                echo "=== Project Files ==="
                pwd
                ls -la

                test -f Dockerfile || (echo "Dockerfile not found"; exit 1)
                test -f requirements.txt || (echo "requirements.txt not found"; exit 1)
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                python3 -m pip install --upgrade pip

                if [ -f requirements.txt ]; then
                    pip3 install -r requirements.txt
                fi

                pip3 install pytest httpx
                '''
            }
        }

        stage('Run Unit Tests') {
            steps {
                sh '''
                if [ -d "tests" ]; then
                    echo "Running Unit Tests..."

                    python3 -m pytest tests/ -v
                else
                    echo "No tests directory found. Skipping..."
                fi
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                docker build -t ${DOCKER_IMAGE}:${BUILD_NUMBER} .
                docker tag ${DOCKER_IMAGE}:${BUILD_NUMBER} ${DOCKER_IMAGE}:latest
                '''
            }
        }

        stage('Trivy Security Scan') {
            steps {
                sh '''
                trivy image --severity HIGH,CRITICAL \
                ${DOCKER_IMAGE}:${BUILD_NUMBER} || true
                '''
            }
        }

        stage('Push Docker Image') {
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
                    -u "$DOCKER_USER" --password-stdin

                    docker push ${DOCKER_IMAGE}:${BUILD_NUMBER}
                    docker push ${DOCKER_IMAGE}:latest

                    docker logout
                    '''
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                sh '''
                export KUBECONFIG=${KUBECONFIG}

                kubectl set image deployment/house-price-api \
                house-price-api=${DOCKER_IMAGE}:${BUILD_NUMBER}

                kubectl rollout status deployment/house-price-api --timeout=300s
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                sh '''
                export KUBECONFIG=${KUBECONFIG}

                echo "=== Deployments ==="
                kubectl get deployments

                echo "=== Pods ==="
                kubectl get pods -o wide

                echo "=== Services ==="
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
            echo '❌ Pipeline failed. Please check Jenkins console logs.'

            sh '''
            export KUBECONFIG=${KUBECONFIG}

            echo "=== Pods ==="
            kubectl get pods || true

            echo "=== Recent Events ==="
            kubectl get events --sort-by=.metadata.creationTimestamp | tail -20 || true
            '''
        }

        always {
            sh '''
            docker image prune -f
            '''
            cleanWs()
        }
    }
}
