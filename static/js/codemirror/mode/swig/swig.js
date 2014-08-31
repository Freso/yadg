// CodeMirror, copyright (c) by Marijn Haverbeke and others
// Distributed under an MIT license: http://codemirror.net/LICENSE

(function(mod) {
  if (typeof exports == "object" && typeof module == "object") // CommonJS
    mod(require("../../lib/codemirror"));
  else if (typeof define == "function" && define.amd) // AMD
    define(["../../lib/codemirror"], mod);
  else // Plain browser env
    mod(CodeMirror);
})(function(CodeMirror) {
  "use strict";

  CodeMirror.defineMode("swig", function() {
    var keywords = ["autoescape", "endautoescape", "block", "endblock", "if",
      "else", "elseif", "endif", "extends", "filter", "endfilter", "for", "endfor",
      "and", "in", "not", "or", "as", "import", "include", "macro", "endmacro",
      "parent", "raw", "endraw", "set", "spaceless", "endspaceless"],
    operator = /^[+\-*&%=<>!?|~^]/,
    sign = /^[:\[\(\{]/,
    atom = ["true", "false"],
    number = /^(\d[+\-\*\/])?\d+(\.\d+)?/;

    keywords = new RegExp("((" + keywords.join(")|(") + "))\\b");
    atom = new RegExp("((" + atom.join(")|(") + "))\\b");

    function tokenBase (stream, state) {
      var ch = stream.peek();

      //Comment
      if (state.incomment) {
        if(!stream.skipTo("#}")) {
          stream.skipToEnd();
        } else {
          stream.eatWhile(/\#|}/);
          state.incomment = false;
        }
        return "comment";
      //Tag
      } else if (state.intag) {
        //After operator
        if(state.operator) {
          state.operator = false;
          if(stream.match(atom)) {
            return "atom";
          }
          if(stream.match(number)) {
            return "number";
          }
        }
        //After sign
        if(state.sign) {
          state.sign = false;
          if(stream.match(atom)) {
            return "atom";
          }
          if(stream.match(number)) {
            return "number";
          }
        }

        if(state.instring) {
          if(ch == state.instring) {
            state.instring = false;
          }
          stream.next();
          return "string";
        } else if(ch == "'" || ch == '"') {
          state.instring = ch;
          stream.next();
          return "string";
        } else if(stream.match(state.intag + "}") || stream.eat("-") && stream.match(state.intag + "}")) {
          state.intag = false;
          return "tag";
        } else if(stream.match(operator)) {
          state.operator = true;
          return "operator";
        } else if(stream.match(sign)) {
          state.sign = true;
        } else {
          if(stream.eat(" ") || stream.sol()) {
            if(stream.match(keywords)) {
              return "keyword";
            }
            if(stream.match(atom)) {
              return "atom";
            }
            if(stream.match(number)) {
              return "number";
            }
            if(stream.sol()) {
              stream.next();
            }
          } else {
            stream.next();
          }

        }
        return "variable";
      } else if (stream.eat("{")) {
        if (ch = stream.eat("#")) {
          state.incomment = true;
          if(!stream.skipTo("#}")) {
            stream.skipToEnd();
          } else {
            stream.eatWhile(/\#|}/);
            state.incomment = false;
          }
          return "comment";
        //Open tag
        } else if (ch = stream.eat(/\{|%/)) {
          //Cache close tag
          state.intag = ch;
          if(ch == "{") {
            state.intag = "}";
          }
          stream.eat("-");
          return "tag";
        }
      }
      stream.next();
    };

    return {
      startState: function () {
        return {tokenize: tokenBase};
      },
      token: function (stream, state) {
        return state.tokenize(stream, state);
      }
    };
  });
});
