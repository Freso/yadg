var sandbox = new JSandbox(),
    templates = {
        {% for name,dep in dependencies.items %}"{{ name|escapejs }}" : "{{ dep.template|escapejs }}",
        {%  endfor %}
    },
    template = "{{ template.template|escapejs }}",
    data = {{ json_data|safe }},
    eval_string = "myswig.render(input.template, { locals: input.data, filename: 'test' + (i++) })";

sandbox.load("{{ STATIC_URL }}js/swig.min.js", function () { // onload
    sandbox.load("{{ STATIC_URL }}js/swig.custom.js", function () {
        this.exec({data: "var myswig = new swig.Swig({ loader: swig.loaders.memory(input.templates), autoescape: false }), i=0; yadg_filters.register_filters(myswig);", input: {templates: templates}});
        this.eval(eval_string, success_callback, {template: template, data: data}, failure_callback);
    });
});