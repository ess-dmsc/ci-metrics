@Library('ecdc-pipeline')
import ecdcpipeline.ContainerBuildNode
import ecdcpipeline.PipelineBuilder

container_build_nodes = [
  'centos7': ContainerBuildNode.getDefaultContainerBuildNode('centos7-gcc8')
]

properties([
  disableConcurrentBuilds(),
  pipelineTriggers([
    [
      $class: 'jenkins.triggers.ReverseBuildTrigger',
      upstreamProjects: "ess-dmsc/event-formation-unit/master",
      threshold: hudson.model.Result.SUCCESS
    ]
  ])
])

pipeline_builder = new PipelineBuilder(this, container_build_nodes)
builders = pipeline_builder.createBuilders { container ->

  pipeline_builder.stage("${container.key}: checkout") {
    dir(pipeline_builder.project) {
      scm_vars = checkout scm
    }
    // Copy source code to container
    container.copyTo(pipeline_builder.project, pipeline_builder.project)
  }  // stage

  pipeline_builder.stage("${container.key}: script") {
    causes = currentBuild.getBuildCauses()
    cause = causes[0]

    upstream = cause["upstreamProject"]
    if(upstream) {
      // upstreamProject is ORG/JOB/BRANCH
      repo = upstream.tokenize("/")[1]
    } else {
      error "Error: failed to identify upstream project"
    }
    build_number = cause["upstreamBuild"]

    container.sh """
      cd ${pipeline_builder.project}/scripts
      python jenkinsmetrics.py ${repo} ${build_number}
    """
  }

}

node('docker') {
  scm_vars = checkout scm
  parallel builders

  // Delete workspace when build is done
  cleanWs()
}
