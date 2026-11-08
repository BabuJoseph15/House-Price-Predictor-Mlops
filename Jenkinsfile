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

        stage('Debug Workspace') {

            steps {

                sh '''
                echo "========== WORKSPACE =========="

                pwd

                ls -la

                echo "========== DVC =========="

                ls -la .dvc || true

                cat .dvc/config || true

                echo "========== K8S =========="

                ls -la k8s || true
                '''
            }
        }

        stage('Verify Files') {

            steps {

                sh '''
                test -f app.py

                test -f Dockerfile

                test -f requirements.txt

                test -f Jenkinsfile

                test -f k8s/deployment.yaml

                test -f k8s/service.yaml
                '''
            }
        }

        stage('Create Virtual Environment') {

            steps {

                sh '''
                python3 -m venv venv

                . venv/bin/activate

                python --version

                pip install --upgrade pip
                '''
            }
        }

        stage('Install Dependencies') {

            steps {

                sh '''
                . venv/bin/activate

                pip install -r requirements.txt
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

        /*
         * TEMPORARILY DISABLED
         * Local DVC works.
         * Jenkins DVC dependency stack requires cleanup.
         */
        stage('DVC Pull') {

            steps {

                echo 'Skipping DVC Pull temporarily'
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

                    sh """
                    ${SCANNER_HOME}/bin/sonar-scanner \
                      -Dsonar.projectKey=House-Price-MLOps \
                      -Dsonar.projectName='House Price MLOps' \
                      -Dsonar.sources=. \
                      -Dsonar.exclusions=venv/**,.dvc/**,mlruns/**,artifacts/**,__pycache__/**,grafana/** \
                      -Dsonar.python.version=3.9
                    """
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

        stage('Verify Kubernetes Secret') {

            steps {

                sh '''
                export KUBECONFIG=${KUBECONFIG}

                kubectl get secret aws-credentials
                '''
            }
        }

        stage('Deploy to Kubernetes') {

            steps {

                sh '''
                export KUBECONFIG=${KUBECONFIG}

                sed -i \
                "s|image: babujoseph5757/house-price-api:.*|image: ${DOCKER_IMAGE}:${BUILD_NUMBER}|g" \
                k8s/deployment.yaml

                kubectl apply -f k8s/deployment.yaml

                kubectl apply -f k8s/service.yaml

                kubectl rollout restart deployment house-price-api

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
