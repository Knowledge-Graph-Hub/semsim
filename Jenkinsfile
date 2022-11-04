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
        BUILDSTARTDATE = sh(script: "echo `date +%Y%m%d`", returnStdout: true).trim()
        S3PROJECTDIR = 'semsim' // no trailing slash

        // Distribution ID for the AWS CloudFront for this bucket
        // used solely for invalidations
        AWS_CLOUDFRONT_DISTRIBUTION_ID = 'EUVSWXZQBXCFP'

        CUTOFF_VALUE = "5"
        MERGEDNAME_BASE = 'kgphenio_hp-vs-mp_semsim_$CUTOFF_VALUE'

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
                    sh "echo $BUILDSTARTDATE > dow.txt"
                    sh "echo $BUILDSTARTDATE"
                    sh "echo $MERGEDNAME_BASE"
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
                    sh './venv/bin/pip install awscli boto3 s3cmd'
                }
            }
        }

        stage('Download ontology and run similarity measurement') {
            steps {
                dir('./gitrepo') {
		            sh '. venv/bin/activate && env && semsim sim KGPhenio -p HP,MP -c $CUTOFF_VALUE'
                    sh 'tar -czvf similarities.tar.gz data/KGPhenio_similarities.tsv graphs/kghub/KGPhenio/current/*'
                }
            }
        }

        stage('Publish') {
            steps {
                dir('./gitrepo') {
                    script {

                        // make sure we aren't going to clobber existing data
                        withCredentials([file(credentialsId: 's3cmd_kg_hub_push_configuration', variable: 'S3CMD_CFG')]) {
                            REMOTE_BUILD_DIR_CONTENTS = sh (
                                script: '. venv/bin/activate && s3cmd -c $S3CMD_CFG ls s3://kg-hub-public-data/$S3PROJECTDIR/$BUILDSTARTDATE/',
                                returnStdout: true
                            ).trim()
                            echo "REMOTE_BUILD_DIR_CONTENTS (THIS SHOULD BE EMPTY): '${REMOTE_BUILD_DIR_CONTENTS}'"
                            if("${REMOTE_BUILD_DIR_CONTENTS}" != ''){
                                echo "Will not overwrite existing remote S3 directory: $S3PROJECTDIR/$BUILDSTARTDATE"
                                sh 'exit 1'
                            } else {
                                echo "remote directory $S3PROJECTDIR/$BUILDSTARTDATE is empty, proceeding"
                            }
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
                                // make $BUILDSTARTDATE/ directory and sync to s3 bucket
                                //
                                sh 'mkdir $BUILDSTARTDATE/'
                                sh 'cp -p similarities.tar.gz $BUILDSTARTDATE/${MERGEDNAME_BASE}.tar.gz'

                                // build the index, then upload to remote
                                sh '. venv/bin/activate && multi_indexer -v --directory $BUILDSTARTDATE --prefix https://kg-hub.berkeleybop.io/$S3PROJECTDIR/$BUILDSTARTDATE -x -u'

                                sh 's3cmd -c $S3CMD_CFG put -pr --acl-public --cf-invalidate $BUILDSTARTDATE s3://kg-hub-public-data/$S3PROJECTDIR/'
                                sh 's3cmd -c $S3CMD_CFG rm -r s3://kg-hub-public-data/$S3PROJECTDIR/current/'
                                sh 's3cmd -c $S3CMD_CFG put -pr --acl-public --cf-invalidate $BUILDSTARTDATE/* s3://kg-hub-public-data/$S3PROJECTDIR/current/'

                                // make index for project dir
                                sh '. venv/bin/activate && multi_indexer -v --prefix https://kg-hub.berkeleybop.io/$S3PROJECTDIR/ -b kg-hub-public-data -r $S3PROJECTDIR -x'
                                sh 's3cmd -c $S3CMD_CFG put -pr --acl-public --cf-invalidate ./index.html s3://kg-hub-public-data/$S3PROJECTDIR/'

                                // Invalidate the CDN now that the new files are up.
                                sh 'echo "[preview]" > ./awscli_config.txt && echo "cloudfront=true" >> ./awscli_config.txt'
                                sh '. venv/bin/activate && AWS_CONFIG_FILE=./awscli_config.txt python3.9 ./venv/bin/aws cloudfront create-invalidation --distribution-id $AWS_CLOUDFRONT_DISTRIBUTION_ID --paths "/*"'

                                // Should now appear at:
                                // https://kg-hub.berkeleybop.io/[artifact name]
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