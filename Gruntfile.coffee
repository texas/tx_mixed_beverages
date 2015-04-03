module.exports = (grunt) ->
  grunt.initConfig
    pkg: grunt.file.readJSON('package.json')
    sass:
      options:
        sourceMap: true
      dist:
        files:
          'mixed_beverages/static/app.css': 'mixed_beverages/static_src/sass/app.sass'
    autoprefixer:
      options:
        browsers: ['last 2 versions']
        diff: true
        map: true
        single_file:
          src: 'mixed_beverages/static/app.css'
          # overwrite original
          dest: 'mixed_beverages/static/app.css'
    jshint:
      all: [
        'mixed_beverages/static_src/js/**/*.js'
      ]
    browserify:
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
        tasks: ['sass', 'autoprefixer']
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
        tasks: ['browserify', 'uglify']
        options:
          spawn: false

  grunt.loadNpmTasks 'grunt-sass'
  grunt.loadNpmTasks 'grunt-autoprefixer'
  grunt.loadNpmTasks 'grunt-contrib-jshint'
  grunt.loadNpmTasks 'grunt-browserify'
  grunt.loadNpmTasks 'grunt-contrib-uglify'
  grunt.loadNpmTasks 'grunt-contrib-watch'

  # build the assets needed
  grunt.registerTask('build', ['sass', 'autoprefixer', 'browserify', 'uglify'])
  # build the assets with sanity checks
  grunt.registerTask('default', ['sass', 'autoprefixer', 'jshint', 'browserify', 'uglify'])
  # build assets and automatically re-build when a file changes
  grunt.registerTask('dev', ['build', 'watch'])
