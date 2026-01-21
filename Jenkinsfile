pipeline {
    agent any

    environment {
        AWS_REGION = 'ap-northeast-2'
        SERVICE_NAME = 'jiaa-server-ai'
        IMAGE_TAG = 'latest'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    dir('jiaa-server-ai') {
                         sh "docker build -t ${SERVICE_NAME}:${IMAGE_TAG} ."
                    }
                }
            }
        }

        stage('Push to ECR') {
            steps {
                script {
                    withAWS(credentials: 'aws-credentials', region: AWS_REGION) {
                        def AWS_ACCOUNT_ID = sh(script: "aws sts get-caller-identity --query Account --output text", returnStdout: true).trim()
                        def ECR_REGISTRY = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
                        
                        sh "aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}"
                        sh "docker tag ${SERVICE_NAME}:${IMAGE_TAG} ${ECR_REGISTRY}/${SERVICE_NAME}:${IMAGE_TAG}"
                        sh "docker push ${ECR_REGISTRY}/${SERVICE_NAME}:${IMAGE_TAG}"
                    }
                }
            }
        }

        stage('Deploy to ECS') {
            steps {
                script {
                    withAWS(credentials: 'aws-credentials', region: AWS_REGION) {
                        sh "aws ecs update-service --cluster jiaa-cluster --service ${SERVICE_NAME} --force-new-deployment"
                    }
                }
            }
        }
    }

    post {
        success {
            echo "Build & Deploy Success: ${env.SERVICE_NAME}:${env.IMAGE_TAG}"
        }
        failure {
            echo "Build Failed: ${env.SERVICE_NAME}"
        }
        always {
            cleanWs()
        }
    }
}
