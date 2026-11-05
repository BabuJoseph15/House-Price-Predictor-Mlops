pipeline {

    agent any

    environment {

        DOCKER_IMAGE = "babujoseph5757/house-price-api"

        IMAGE_TAG = "${BUILD_NUMBER}"

        KUBECONFIG = "/var/lib/jenkins/.kube/config"

        TRIVY_TEMP_DIR = "/var/lib/jenkins/trivy-temp"

        EMAIL_RECIPIENT = "babu.joseph5757@gmail.com"
    }

    stages {

        stage('Checkout Source') {

            steps {
                checkout scm
            }
        }

        stage('SonarQube Analysis') {

            steps {

                withSonarQubeEnv('sonarqube-server') {

                    withCredentials([
                        string(
                            credentialsId: 'house-price-sonar-token',
                            variable: 'SONAR_TOKEN'
                        )
                    ]) {

                        sh '''
                        sonar-scanner \
                        -Dsonar.projectKey=house-price-mlops \
                        -Dsonar.projectName="House Price MLOps" \
                        -Dsonar.host.url=$SONAR_HOST_URL \
                        -Dsonar.token=$SONAR_TOKEN
                        '''
                    }
                }
            }
        }

        stage('Quality Gate') {

            steps {

                timeout(
                    time: 10,
                    unit: 'MINUTES'
                ) {

                    waitForQualityGate abortPipeline: false
                }
            }
        }

        stage('Run Unit Tests') {

            steps {

                sh '''
                if [ -d tests ]; then
                    python3 -m pytest tests/ -v
                else
                    echo "No tests found. Skipping..."
                fi
                '''
            }
        }

        stage('Build Docker Image') {

            steps {

                sh '''
                docker build \
                -t ${DOCKER_IMAGE}:${IMAGE_TAG} \
                .
                '''
            }
        }

        stage('Trivy Scan') {

            steps {

                sh '''
                mkdir -p ${TRIVY_TEMP_DIR}

                export TMPDIR=${TRIVY_TEMP_DIR}

                trivy image \
                --timeout 20m \
                --skip-version-check \
                --scanners vuln \
                --severity HIGH,CRITICAL \
                --exit-code 0 \
                ${DOCKER_IMAGE}:${IMAGE_TAG}
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
                docker push ${DOCKER_IMAGE}:${IMAGE_TAG}

                docker tag \
                ${DOCKER_IMAGE}:${IMAGE_TAG} \
                ${DOCKER_IMAGE}:latest

                docker push ${DOCKER_IMAGE}:latest
                '''
            }
        }

        stage('Deploy To Kubernetes') {

            steps {

                sh '''
                kubectl set image deployment/house-price-api \
                house-price-api=${DOCKER_IMAGE}:${IMAGE_TAG}

                kubectl rollout status deployment/house-price-api \
                --timeout=300s
                '''
            }
        }
    }

    post {

        success {

            emailext(
                to: "${EMAIL_RECIPIENT}",
                subject: "SUCCESS - ${JOB_NAME} #${BUILD_NUMBER}",
                body: """
House Price Pipeline Successful

Build Number: ${BUILD_NUMBER}

Build URL:
${BUILD_URL}
"""
            )
        }

        failure {

            emailext(
                to: "${EMAIL_RECIPIENT}",
                subject: "FAILED - ${JOB_NAME} #${BUILD_NUMBER}",
                body: """
House Price Pipeline Failed

Build URL:
${BUILD_URL}
"""
            )
        }

        always {

            sh '''
            docker builder prune -f || true
            docker container prune -f || true
            docker image prune -f || true
            '''

            cleanWs()
        }
    }
}
