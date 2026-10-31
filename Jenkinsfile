pipeline {

    agent any

    environment {

        DOCKER_IMAGE = "babujoseph5757/house-price-api"

        IMAGE_TAG = "${BUILD_NUMBER}"

        KUBECONFIG = "/var/lib/jenkins/.kube/config"

        TRIVY_TEMP_DIR = "/var/lib/jenkins/trivy-temp"

        PATH = "/var/lib/jenkins/.local/bin:${env.PATH}"
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

                echo "Checking out House Price source code..."

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

        stage('Install Dependencies') {

            steps {

                sh '''
                python3 --version

                python3 -m pip install --upgrade pip

                if [ -f requirements.txt ]; then
                    python3 -m pip install \
                    --user \
                    --no-cache-dir \
                    -r requirements.txt
                fi
                '''
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

                echo "Building Docker image..."

                sh '''
                docker build \
                -t ${DOCKER_IMAGE}:${IMAGE_TAG} .
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
                --timeout=300s
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
                subject: "✅ SUCCESS - House Price MLOps Pipeline #${BUILD_NUMBER}",
                body: """
Build Successful

Job Name: ${JOB_NAME}
Build Number: ${BUILD_NUMBER}

Docker Image:
${DOCKER_IMAGE}:${IMAGE_TAG}

Status:
SUCCESS

Build URL:
${BUILD_URL}
                """,
                to: "babu.joseph5757@gmail.com"
            )

            echo '✅ House Price deployment successful'
        }

        failure {

            emailext(
                subject: "❌ FAILED - House Price MLOps Pipeline #${BUILD_NUMBER}",
                body: """
Build Failed

Job Name: ${JOB_NAME}
Build Number: ${BUILD_NUMBER}

Please review Jenkins logs.

Build URL:
${BUILD_URL}
                """,
                to: "babu.joseph5757@gmail.com"
            )

            echo '❌ Pipeline failed'
        }

        always {

            sh '''
            rm -rf ~/.cache/pip || true

            rm -rf ${TRIVY_TEMP_DIR}/* || true

            docker container prune -f || true

            docker image prune -f || true

            docker builder prune -f || true
            '''

            cleanWs()
        }
    }
}
