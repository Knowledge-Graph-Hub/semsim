pipeline {
    agent {
        docker {
            reuseNode false
            image 'caufieldjh/ubuntu20-python-3-9-14-dev:2'
        }
    }
    triggers{
        cron('H H 1 1-12 *')
    }
    environment {
        S3PROJECTDIR = 'kg-phenio' // no trailing slash
        // this is the source graph directory

        // Distribution ID for the AWS CloudFront for this bucket
        // used solely for invalidations
        AWS_CLOUDFRONT_DISTRIBUTION_ID = 'EUVSWXZQBXCFP'

        CUTOFF_VALUE = "5"
        SEMSIM_OUT_BASE = 'kg-phenio_hp-vs-mp_semsim_$CUTOFF_VALUE'

    }
    options {
        timestamps()
        disableConcurrentBuilds()
    }
    stages {
        // Very first: pause for a minute to give a chance to
        // cancel and clean the workspace before use.
        stage('Ready and clean') {
            steps {
                // Give us a minute to cancel if we want.
                sleep time: 30, unit: 'SECONDS'
            }
        }

        stage('Initialize') {
            steps {
                // print some info
                dir('./gitrepo') {
                    sh 'env > env.txt'
                    sh 'echo $BRANCH_NAME > branch.txt'
                    sh 'echo "$BRANCH_NAME"'
                    sh 'cat env.txt'
                    sh 'cat branch.txt'
                    sh "echo $SEMSIM_OUT_BASE"
                    sh "python3.9 --version"
                    sh "id"
                    sh "whoami" // this should be jenkinsuser
                    // if the above fails, then the docker host didn't start the docker
                    // container as a user that this image knows about. This will
                    // likely cause lots of problems (like trying to write to $HOME
                    // directory that doesn't exist, etc), so we should fail here and
                    // have the user fix this

                }
            }
        }

        stage('Build semsim') {
            steps {
                dir('./gitrepo') {
                    git(
                            url: 'https://github.com/Knowledge-Graph-Hub/semsim',
                            branch: env.BRANCH_NAME
                    )
                    sh '/usr/bin/python3.9 -m venv venv'
                    sh '. venv/bin/activate'
                    // Now move on to the actual install + reqs
                    sh './venv/bin/pip install .'
                    sh './venv/bin/pip install awscli boto3 s3cmd multi-indexer'
                }
            }
        }

        stage('Download ontology and run similarity measurement') {
            steps {
                dir('./gitrepo') {
                    script {
                        sh 'mkdir graphs && wget https://kg-hub.berkeleybop.io/kg-phenio/current/kg-phenio.tar.gz -P graphs/'
                        sh 'wget https://kg-hub.berkeleybop.io/kg-phenio/current/index.html' // Needed to get graph version
                        sh '. venv/bin/activate && env && semsim sim KGPhenio -p HP,MP -c $CUTOFF_VALUE -i graphs/kg-phenio.tar.gz'
                        sh 'tar -czvf similarities.tar.gz data/KGPhenio_similarities graphs/kg-phenio.tar.gz'

                        // Set the KGBUILDDATE to the downloaded build of the graph
                        KGBUILDDATE = sh (
                            script: 'grep "<title>" index.html | cut -d/ -f5',
                            returnStdout: true
                        ).trim()
                        echo KGBUILDDATE

                        sh 'rm index.html'
                    }
                }
            }
        }

        stage('Publish') {
            steps {
                dir('./gitrepo') {
                    script {
                        withCredentials([file(credentialsId: 's3cmd_kg_hub_push_configuration', variable: 'S3CMD_CFG')]) {
                            REMOTE_BUILD_DIR_CONTENTS = sh (
                                script: '. venv/bin/activate && s3cmd -c $S3CMD_CFG ls s3://kg-hub-public-data/$S3PROJECTDIR/$KGBUILDDATE/',
                                returnStdout: true
                            ).trim()
                            echo "REMOTE_BUILD_DIR_CONTENTS: '${REMOTE_BUILD_DIR_CONTENTS}'"
                        }

                        if (env.BRANCH_NAME != 'main') {
                            echo "Will not push if not on correct branch."
                        } else {
                            withCredentials([
					            file(credentialsId: 's3cmd_kg_hub_push_configuration', variable: 'S3CMD_CFG'),
					            file(credentialsId: 'aws_kg_hub_push_json', variable: 'AWS_JSON'),
					            string(credentialsId: 'aws_kg_hub_access_key', variable: 'AWS_ACCESS_KEY_ID'),
					            string(credentialsId: 'aws_kg_hub_secret_key', variable: 'AWS_SECRET_ACCESS_KEY')]) {
                                           
                                //
                                // Upload the results to the S3 bucket where the existing graph is stored.
                                //
                                sh 'mkdir $KGBUILDDATE/'
                                sh 'cp -p similarities.tar.gz $KGBUILDDATE/${SEMSIM_OUT_BASE}.tar.gz'

                                sh 's3cmd -c $S3CMD_CFG put -pr --acl-public --cf-invalidate $KGBUILDDATE/${SEMSIM_OUT_BASE}.tar.gz s3://kg-hub-public-data/$S3PROJECTDIR/$KGBUILDDATE/${SEMSIM_OUT_BASE}.tar.gz'

                                // update indices and upload
                                sh '. venv/bin/activate && multi_indexer -v --prefix https://kg-hub.berkeleybop.io/$S3PROJECTDIR/$KGBUILDDATE/ -b kg-hub-public-data -r $S3PROJECTDIR/$KGBUILDDATE -x'
                                sh 's3cmd -c $S3CMD_CFG put -pr --acl-public --cf-invalidate ./index.html s3://kg-hub-public-data/$S3PROJECTDIR/$KGBUILDDATE/'
                                sh 's3cmd -c $S3CMD_CFG put -pr --acl-public --cf-invalidate ./index.html s3://kg-hub-public-data/$S3PROJECTDIR/current/'

                                // Invalidate the CDN now that the new files are up.
                                sh 'echo "[preview]" > ./awscli_config.txt && echo "cloudfront=true" >> ./awscli_config.txt'
                                sh '. venv/bin/activate && AWS_CONFIG_FILE=./awscli_config.txt python3.9 ./venv/bin/aws cloudfront create-invalidation --distribution-id $AWS_CLOUDFRONT_DISTRIBUTION_ID --paths "/*"'

                            }

                        }
                    }
                }
            }
        }        
    }

    post {
        always {
            echo 'In always'
            echo 'Cleaning workspace...'
            cleanWs()
        }
        success {
            echo 'I succeeded!'
        }
        unstable {
            echo 'I am unstable :/'
        }
        failure {
            echo 'I failed :('
        }
        changed {
            echo 'Things were different before...'
        }
    }

}