pipeline {
  agent { label 'home' }
    environment {
        IMAGE           = 'dzailz/sr_tg_bot:latest'
        CONTAINER_NAME  = 'sr_tg_bot'
    }

  stages {
    stage('prepare') {
    steps {
      sh '''
        docker_image_id=$(docker images -q "${IMAGE}")

        if [ -n "$docker_image_id" ]; then
            if [ "$(docker stop ${CONTAINER_NAME})" ]; then
                echo "container stopped"
            fi

            if [ "$(docker rmi "$docker_image_id" -f)" ]; then
                echo "image removed"
            fi
        fi
      '''
      }
    }

    stage('run') {
      steps {
        sh 'docker run -d --env-file /var/tg_bot/.env --name "${CONTAINER_NAME}" --rm "${IMAGE}"'
      }
    }

    stage('test') {
      steps {
        sh '''
        attempt_counter=0
        max_attempts=10

        until { docker logs "${CONTAINER_NAME}" 2>&1 | grep "INFO - Start polling."; } do
            if [ ${attempt_counter} -eq ${max_attempts} ];then
              echo "Max attempts reached"
              exit 1
            fi

            printf '.'
            attempt_counter=$((attempt_counter + 1))
            sleep 1
        done
        '''
      }
    }
  }
}
