@Library('ecdc-pipeline')
import ecdcpipeline.ContainerBuildNode
import ecdcpipeline.PipelineBuilder

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

container_build_nodes = [
  'centos7': ContainerBuildNode.getDefaultContainerBuildNode('centos7-gcc11')
]

pipeline_builder = new PipelineBuilder(this, container_build_nodes)
builders = pipeline_builder.createBuilders { container ->

  pipeline_builder.stage("${container.key}: checkout") {
    dir(pipeline_builder.project) {
      scm_vars = checkout scm
    }
    // Copy source code to container
    container.copyTo(pipeline_builder.project, pipeline_builder.project)
  }  // stage

  pipeline_builder.stage("${container.key}: dependencies") {
    container.sh "python -m pip install --user requests"
  }  // stage

  pipeline_builder.stage("${container.key}: script") {
    causes = currentBuild.getBuildCauses()

    for (c in causes) {
      c_class = c["_class"]
      if (c_class == 'hudson.model.Cause$UpstreamCause') {
        // upstreamProject is ORG/REPO/BRANCH
        repo = c["upstreamProject"].tokenize("/")[1]
        build_number = c["upstreamBuild"]

        container.sh """
          cd ${pipeline_builder.project}/scripts
          python jenkinsmetrics.py -r ${repo} -b ${build_number}
        """
      } else {
        // Ignore build causes such as pushing to this repository
        echo "Ignoring build cause ${c_class}"
      }  // if/else
    }  // for
  }  // stage

}

node('docker') {
  scm_vars = checkout scm
  parallel builders

  // Delete workspace when build is done
  cleanWs()
}
