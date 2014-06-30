// CodeMirror, copyright (c) by Marijn Haverbeke and others
// Distributed under an MIT license: http://codemirror.net/LICENSE

(function(mod) {
  if (typeof exports == "object" && typeof module == "object") // CommonJS
    mod(require("../lib/codemirror"));
  else if (typeof define == "function" && define.amd) // AMD
    define(["../lib/codemirror"], mod);
  else // Plain browser env
    mod(CodeMirror);
})(function(CodeMirror) {
  "use strict";
  CodeMirror.keyMap["default"]["F11"] = function(cm) {
    cm.setOption("fullScreen", !cm.getOption("fullScreen"));
  };
  
  CodeMirror.keyMap["default"]["Esc"] = function(cm) {
    if (cm.getOption("fullScreen")) cm.setOption("fullScreen", false);
  };
});
