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
                pwd
                ls -la

                test -f Dockerfile
                test -f requirements.txt
                test -f app.py
                '''
            }
        }

        stage('Create Python Environment') {
            steps {
                sh '''
                python3 -m venv venv

                . venv/bin/activate

                python --version
                pip --version

                pip install --upgrade pip
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                . venv/bin/activate

                pip install -r requirements.txt
                pip install pytest httpx
                '''
            }
        }

        stage('Validate Dependencies') {
            steps {
                sh '''
                . venv/bin/activate

                pip check
                '''
            }
        }

        stage('Run Unit Tests') {
            steps {
                sh '''
                . venv/bin/activate

                export PYTHONPATH=$WORKSPACE

                pytest tests/ -v
                '''
            }
        }

        stage('Disk Usage Check') {
            steps {
                sh '''
                echo "===== DISK USAGE ====="
                df -h

                echo "===== DOCKER USAGE ====="
                docker system df || true
                '''
            }
        }

        stage('Docker Cleanup') {
            steps {
                sh '''
                docker image prune -a -f || true
                docker builder prune -a -f || true
                docker volume prune -f || true
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                docker build --no-cache \
                -t ${DOCKER_IMAGE}:${BUILD_NUMBER} .

                docker tag \
                ${DOCKER_IMAGE}:${BUILD_NUMBER} \
                ${DOCKER_IMAGE}:latest
                '''
            }
        }

        stage('Trivy Security Scan') {
            steps {
                sh '''
                trivy image \
                --severity HIGH,CRITICAL \
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
                    -u "$DOCKER_USER" \
                    --password-stdin

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

                kubectl rollout status deployment/house-price-api \
                --timeout=300s
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                sh '''
                export KUBECONFIG=${KUBECONFIG}

                kubectl get deployments
                kubectl get pods -o wide
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
            echo '❌ Pipeline failed. Collecting diagnostics...'

            sh '''
            df -h || true

            docker system df || true

            export KUBECONFIG=${KUBECONFIG}

            kubectl get pods || true
            kubectl get deployments || true

            kubectl get events \
            --sort-by=.metadata.creationTimestamp | tail -20 || true
            '''
        }

        always {
            sh '''
            docker image prune -a -f || true
            docker builder prune -a -f || true
            docker volume prune -f || true
            '''
            cleanWs()
        }
    }
}
