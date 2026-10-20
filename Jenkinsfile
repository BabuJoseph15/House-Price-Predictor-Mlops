pipeline {

    agent any

    environment {

        DOCKER_IMAGE = "babujoseph5757/house-price-api"

        IMAGE_TAG = "${BUILD_NUMBER}"

        KUBECONFIG = "/var/lib/jenkins/.kube/config"
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

        stage('Checkout Source Code') {

            steps {

                echo 'Cloning repository...'

                git(
                    branch: 'master',
                    url: 'https://github.com/BabuJoseph15/House-Price-Predictor-Mlops.git'
                )
            }
        }

        stage('Verify Files') {

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

                if [ -f requirements.txt ]; then
                    pip3 install -r requirements.txt
                fi
                '''
            }
        }

        stage('Run Unit Tests') {

            steps {

                sh '''
                if [ -d tests ]; then
                    pytest tests/
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
                -t $DOCKER_IMAGE:$IMAGE_TAG \
                .
                '''
            }
        }

        stage('Security Scan - Trivy') {

            steps {

                sh '''
                trivy image \
                --severity HIGH,CRITICAL \
                --exit-code 0 \
                $DOCKER_IMAGE:$IMAGE_TAG
                '''
            }
        }

        stage('Docker Login') {

            steps {

                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-cred',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )
                ]) {

                    sh '''
                    echo "$DOCKER_PASS" | \
                    docker login \
                    -u "$DOCKER_USER" \
                    --password-stdin
                    '''
                }
            }
        }

        stage('Push Docker Image') {

            steps {

                sh '''
                docker push $DOCKER_IMAGE:$IMAGE_TAG

                docker tag \
                $DOCKER_IMAGE:$IMAGE_TAG \
                $DOCKER_IMAGE:latest

                docker push \
                $DOCKER_IMAGE:latest
                '''
            }
        }

        stage('Deploy To Kubernetes') {

            steps {

                sh '''
                kubectl set image deployment/house-price-api \
                house-price-api=$DOCKER_IMAGE:$IMAGE_TAG

                kubectl rollout status deployment/house-price-api \
                --timeout=300s
                '''
            }
        }

        stage('Verify Deployment') {

            steps {

                sh '''
                echo "Current Pods"

                kubectl get pods

                echo "Current Services"

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
        }

        always {

            sh '''
            docker image prune -f
            '''

            cleanWs()
        }
    }
}
