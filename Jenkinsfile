 node {
    withDockerRegistry([credentialsId: '9a67dc8e-fec4-480c-872f-e62a0c8811f6', url: 'https://docker-registry.services.iit.cnr.it']) {
        git branch: '$BRANCH_NAME', credentialsId: 'cdbeed4b-cf30-488a-8e6a-edbe9ca0e319', url: 'ssh://git@gitlab.tools.iit.cnr.it:10022/epas/epas-client.git'
    
        sh "git rev-parse HEAD > .git/commit-id"
        def commit_id = readFile('.git/commit-id').trim()
        println commit_id
    
        stage "build"
        def app = docker.build "docker-registry.services.iit.cnr.it/epas/epas-client"
    
        stage "publish"
        app.push '$BRANCH_NAME'
    }
}