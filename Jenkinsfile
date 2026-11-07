pipeline {

    agent any

    environment {

        DOCKER_IMAGE = "babujoseph5757/house-price-api"

        KUBECONFIG = "/var/lib/jenkins/.kube/config"

        DVC_BIN = "/var/lib/jenkins/.local/bin/dvc"

        SCANNER_HOME = tool 'sonar-scanner'

        TRIVY_TEMP_DIR = "/var/lib/jenkins/trivy-temp"

        AWS_DEFAULT_REGION = "ap-south-1"
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

                test -f app.py
                test -f Dockerfile
                test -f requirements.txt
                test -f deployment.yaml
                test -f service.yaml
                '''
            }
        }

        stage('Install Dependencies') {

            steps {

                sh '''
                python3 -m venv venv

                . venv/bin/activate

                python --version

                pip install --upgrade pip

                pip install -r requirements.txt

                pip check
                '''
            }
        }

        stage('DVC Pull') {

            steps {

                withCredentials([
                    string(
                        credentialsId: 'aws-access-key-id',
                        variable: 'AWS_ACCESS_KEY_ID'
                    ),
                    string(
                        credentialsId: 'aws-secret-access-key',
                        variable: 'AWS_SECRET_ACCESS_KEY'
                    )
                ]) {

                    sh '''
                    export PATH=/var/lib/jenkins/.local/bin:$PATH

                    ${DVC_BIN} doctor

                    ${DVC_BIN} pull
                    '''
                }
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

        stage('SonarQube Analysis') {

            steps {

                withSonarQubeEnv('sonarqube-server') {

                    sh '''
                    ${SCANNER_HOME}/bin/sonar-scanner \
                      -Dsonar.projectKey=House-Price-MLOps \
                      -Dsonar.projectName="House Price MLOps" \
                      -Dsonar.sources=. \
                      -Dsonar.python.version=3.9
                    '''
                }
            }
        }

        stage('Quality Gate') {

            steps {

                timeout(
                    time: 10,
                    unit: 'MINUTES'
                ) {

                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Build Docker Image') {

            steps {

                sh '''
                docker build \
                  -t ${DOCKER_IMAGE}:${BUILD_NUMBER} .

                docker tag \
                  ${DOCKER_IMAGE}:${BUILD_NUMBER} \
                  ${DOCKER_IMAGE}:latest
                '''
            }
        }

        stage('Prepare Trivy Temp Directory') {

            steps {

                sh '''
                mkdir -p ${TRIVY_TEMP_DIR}
                '''
            }
        }

        stage('Trivy Security Scan') {

            steps {

                sh '''
                export TMPDIR=${TRIVY_TEMP_DIR}

                trivy image \
                  --timeout 30m \
                  --skip-version-check \
                  --scanners vuln \
                  --severity HIGH,CRITICAL \
                  --exit-code 0 \
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

        stage('Application Health Check') {

            steps {

                sh '''
                MINIKUBE_IP=$(minikube ip)

                curl -f \
                  http://${MINIKUBE_IP}:30080/health
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
                --sort-by=.metadata.creationTimestamp \
                | tail -20 || true
            '''
        }

        always {

            sh '''
            docker image prune -f || true

            docker builder prune -f || true
            '''

            cleanWs()
        }
    }
}
