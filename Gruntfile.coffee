module.exports = (grunt) ->
  grunt.initConfig
    pkg: grunt.file.readJSON('package.json')
    sass:
      dist:
        files:
          'mixed_beverages/static/app.css': 'mixed_beverages/static_src/sass/app.sass'
    postcss:
      options:
        processors: [
          require('autoprefixer')({browsers: 'last 2 versions'}),
        ]
      dist:
        src: 'mixed_beverages/static/app.css'
    eslint:
      all: [
        'mixed_beverages/static_src/js/**/*.js'
      ]
    browserify:
      options:
        transform: ['babelify']
      app:
        files:
          'mixed_beverages/static/app.js': 'mixed_beverages/static_src/js/app.js'
    uglify:
      app:
        files:
          'mixed_beverages/static/app.min.js': ['mixed_beverages/static/app.js']
    watch:
      # use live reload if the browser has it
      # if you don't have it you can get it here:
      # http://feedback.livereload.com/knowledgebase/articles/86242-how-do-i-install-and-use-the-browser-extensions-
      options:
        livereload: true
      sass:
        files: ['mixed_beverages/static_src/sass/**/*.sass']
        tasks: ['sass', 'postcss']
        options:
          livereload: false
          # spawn has to be on or else the css watch won't catch changes
          spawn: true
      css:
        files: ['mixed_beverages/static/*.css']
        options:
          spawn: false
      scripts:
        files: ['mixed_beverages/static_src/**/*.js']
        tasks: ['browserify']
        options:
          spawn: false

  grunt.loadNpmTasks 'grunt-sass'
  grunt.loadNpmTasks 'grunt-postcss'
  grunt.loadNpmTasks 'grunt-eslint'
  grunt.loadNpmTasks 'grunt-browserify'
  grunt.loadNpmTasks 'grunt-contrib-uglify'
  grunt.loadNpmTasks 'grunt-contrib-watch'

  # build the assets needed
  grunt.registerTask('build', ['sass', 'postcss', 'browserify', 'uglify'])
  # build the assets with sanity checks
  grunt.registerTask('default', ['build'])
  # build assets and automatically re-build when a file changes
  grunt.registerTask('dev', ['build', 'watch'])
