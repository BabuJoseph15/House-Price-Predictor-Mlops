pipeline {

    agent any

    environment {

        PATH = "/var/lib/jenkins/.local/bin:${env.PATH}"

        DOCKER_IMAGE = "babujoseph5757/house-price-api"

        IMAGE_TAG = "${BUILD_NUMBER}"

        KUBECONFIG = "/var/lib/jenkins/.kube/config"

        TRIVY_TEMP_DIR = "/var/lib/jenkins/trivy-temp"

        EMAIL_RECIPIENT = "babu.joseph5757@gmail.com"
    }

    options {

        timestamps()

        buildDiscarder(
            logRotator(
                numToKeepStr: '10'
            )
        )
    }

    stages {

        stage('Checkout Source') {

            steps {
                checkout scm
            }
        }

        stage('Verify Workspace') {

            steps {

                sh '''
                pwd
                ls -ltr
                '''
            }
        }

        stage('Verify DVC') {

            steps {

                sh '''
                /var/lib/jenkins/.local/bin/dvc version

                /var/lib/jenkins/.local/bin/dvc remote list
                '''
            }
        }

        stage('DVC Pull') {

            steps {

                sh '''
                /var/lib/jenkins/.local/bin/dvc pull
                '''
            }
        }

        stage('SonarQube Analysis') {

            steps {

                script {

                    def scannerHome = tool 'sonar-scanner'

                    withSonarQubeEnv('sonarqube-server') {

                        sh """
                        ${scannerHome}/bin/sonar-scanner \
                        -Dsonar.projectKey=House-Price-MLOps \
                        -Dsonar.projectName='House Price MLOps'
                        """
                    }
                }
            }
        }

        stage('Quality Gate') {

            steps {

                timeout(
                    time: 30,
                    unit: 'MINUTES'
                ) {

                    waitForQualityGate(
                        abortPipeline: false
                    )
                }
            }
        }

        stage('Run Unit Tests') {

            steps {

                sh '''
                if [ -d tests ]; then
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
                docker build \
                -t ${DOCKER_IMAGE}:${IMAGE_TAG} \
                .
                '''
            }
        }

        stage('Trivy Security Scan') {

            steps {

                sh '''
                mkdir -p ${TRIVY_TEMP_DIR}

                export TMPDIR=${TRIVY_TEMP_DIR}

                trivy image \
                --timeout 30m \
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
                --timeout=900s
                '''
            }
        }

        stage('Verify Deployment') {

            steps {

                sh '''
                echo "===== Deployments ====="
                kubectl get deployment

                echo "===== Pods ====="
                kubectl get pods

                echo "===== Services ====="
                kubectl get svc

                echo "===== Current Image ====="
                kubectl describe deployment house-price-api | grep Image
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
House Price MLOps Pipeline Successful

Job Name     : ${JOB_NAME}
Build Number : ${BUILD_NUMBER}

Docker Image:
${DOCKER_IMAGE}:${IMAGE_TAG}

Build URL:
${BUILD_URL}

Regards,
Jenkins
"""
            )
        }

        failure {

            emailext(
                to: "${EMAIL_RECIPIENT}",
                subject: "FAILED - ${JOB_NAME} #${BUILD_NUMBER}",
                body: """
House Price MLOps Pipeline Failed

Job Name     : ${JOB_NAME}
Build Number : ${BUILD_NUMBER}

Build URL:
${BUILD_URL}

Please review Jenkins console logs.

Regards,
Jenkins
"""
            )
        }

        always {

            sh '''
            rm -rf ${TRIVY_TEMP_DIR}/* || true

            docker container prune -f || true

            docker image prune -f || true

            docker builder prune -f || true
            '''

            cleanWs()
        }
    }
}
