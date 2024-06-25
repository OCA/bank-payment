var Plaid = (function (t) {
  function webpackJsonpCallback(r) {
    for (var i, a, u = r[0], l = r[1], d = 0, p = []; d < u.length; d++)
      (a = u[d]),
        Object.prototype.hasOwnProperty.call(o, a) && o[a] && p.push(o[a][0]),
        (o[a] = 0);
    for (i in l) Object.prototype.hasOwnProperty.call(l, i) && (t[i] = l[i]);
    for (c && c(r); p.length; ) p.shift()();
  }
  var r = {},
    o = {32: 0, 7: 0};
  function __webpack_require__(o) {
    if (r[o]) return r[o].exports;
    var i = (r[o] = {i: o, l: !1, exports: {}});

    return (
      t[o].call(i.exports, i, i.exports, __webpack_require__), (i.l = !0), i.exports
    );
  }
  (__webpack_require__.e = function requireEnsure(t) {
    var r = [],
      i = o[t];
    if (0 !== i)
      if (i) r.push(i[2]);
      else {
        var a = new Promise(function (r, a) {
          i = o[t] = [r, a];
        });
        r.push((i[2] = a));
        var u,
          c = document.createElement("script");
        (c.charset = "utf-8"),
          (c.timeout = 120),
          __webpack_require__.nc && c.setAttribute("nonce", __webpack_require__.nc),
          (c.src = (function jsonpScriptSrc(t) {
            return (
              __webpack_require__.p +
              "" +
              ({
                11: "vendors~LazyLink~web3Bridge",
                17: "CBWalletWeb3",
                18: "CBWalletWeb3Storage",
                21: "MEWConnectClient",
                23: "WCV2Web3",
                24: "WCWeb3",
                26: "chainUtilities",
                28: "ethers",
                39: "vendors~CBWalletWeb3",
                42: "vendors~TrezorProvider",
                43: "vendors~WCV2Web3",
                44: "vendors~WCWeb3",
                45: "vendors~ethers",
                48: "web3Bridge",
              }[t] || t) +
              ".js"
            );
          })(t));
        var l = new Error();
        u = function (r) {
          (c.onerror = c.onload = null), clearTimeout(d);
          var i = o[t];
          if (0 !== i) {
            if (i) {
              var a = r && ("load" === r.type ? "missing" : r.type),
                u = r && r.target && r.target.src;
              (l.message = "Loading chunk " + t + " failed.\n(" + a + ": " + u + ")"),
                (l.name = "ChunkLoadError"),
                (l.type = a),
                (l.request = u),
                i[1](l);
            }
            o[t] = void 0;
          }
        };
        var d = setTimeout(function () {
          u({type: "timeout", target: c});
        }, 12e4);
        (c.onerror = c.onload = u), document.head.appendChild(c);
      }
    return Promise.all(r);
  }),
    (__webpack_require__.m = t),
    (__webpack_require__.c = r),
    (__webpack_require__.d = function (t, r, o) {
      __webpack_require__.o(t, r) ||
        Object.defineProperty(t, r, {enumerable: !0, get: o});
    }),
    (__webpack_require__.r = function (t) {
      "undefined" != typeof Symbol &&
        Symbol.toStringTag &&
        Object.defineProperty(t, Symbol.toStringTag, {value: "Module"}),
        Object.defineProperty(t, "__esModule", {value: !0});
    }),
    (__webpack_require__.t = function (t, r) {
      if ((1 & r && (t = __webpack_require__(t)), 8 & r)) return t;
      if (4 & r && "object" == typeof t && t && t.__esModule) return t;
      var o = Object.create(null);
      if (
        (__webpack_require__.r(o),
        Object.defineProperty(o, "default", {enumerable: !0, value: t}),
        2 & r && "string" != typeof t)
      )
        for (var i in t)
          __webpack_require__.d(
            o,
            i,
            function (r) {
              return t[r];
            }.bind(null, i)
          );
      return o;
    }),
    (__webpack_require__.n = function (t) {
      var r =
        t && t.__esModule
          ? function getDefault() {
              return t.default;
            }
          : function getModuleExports() {
              return t;
            };
      return __webpack_require__.d(r, "a", r), r;
    }),
    (__webpack_require__.o = function (t, r) {
      return Object.prototype.hasOwnProperty.call(t, r);
    }),
    (__webpack_require__.p = "/link/2.0.1951/"),
    (__webpack_require__.oe = function (t) {
      throw (console.error(t), t);
    });
  var i = (window.webpackJsonpPlaid = window.webpackJsonpPlaid || []),
    a = i.push.bind(i);
  (i.push = webpackJsonpCallback), (i = i.slice());
  for (var u = 0; u < i.length; u++) webpackJsonpCallback(i[u]);
  var c = a;
  return __webpack_require__((__webpack_require__.s = 1489));
})([
  ,
  function (t, r, o) {
    "use strict";
    var i = o(5),
      a = o(15),
      u = o(43).f;
    i(
      {target: "Object", stat: !0, forced: Object.defineProperty !== u, sham: !a},
      {defineProperty: u}
    );
  },
  function (t, r) {
    (t.exports = function _interopRequireDefault(t) {
      return t && t.__esModule ? t : {default: t};
    }),
      (t.exports.__esModule = !0),
      (t.exports.default = t.exports);
  },
  function (t, r, o) {
    "use strict";
    var i = o(199),
      a = o(40),
      u = o(349);
    i || a(Object.prototype, "toString", u, {unsafe: !0});
  },
  ,
  function (t, r, o) {
    "use strict";
    var i = o(13),
      a = o(94).f,
      u = o(81),
      c = o(40),
      l = o(196),
      d = o(222),
      p = o(144);
    t.exports = function (t, r) {
      var o,
        v,
        h,
        y,
        _,
        g = t.target,
        b = t.global,
        E = t.stat;
      if ((o = b ? i : E ? i[g] || l(g, {}) : i[g] && i[g].prototype))
        for (v in r) {
          if (
            ((y = r[v]),
            (h = t.dontCallGetSet ? (_ = a(o, v)) && _.value : o[v]),
            !p(b ? v : g + (E ? "." : "#") + v, t.forced) && void 0 !== h)
          ) {
            if (typeof y == typeof h) continue;
            d(y, h);
          }
          (t.sham || (h && h.sham)) && u(y, "sham", !0), c(o, v, y, t);
        }
    };
  },
  function (t, r, o) {
    "use strict";
    t.exports = function (t) {
      try {
        return !!t();
      } catch (t) {
        return !0;
      }
    };
  },
  function (t, r, o) {
    "use strict";
    var i = o(147),
      a = Function.prototype,
      u = a.call,
      c = i && a.bind.bind(u, u);
    t.exports = i
      ? c
      : function (t) {
          return function () {
            return u.apply(t, arguments);
          };
        };
  },
  function (t, r, o) {
    var i = o(275);
    (t.exports = function _defineProperty(t, r, o) {
      return (
        (r = i(r)) in t
          ? Object.defineProperty(t, r, {
              value: o,
              enumerable: !0,
              configurable: !0,
              writable: !0,
            })
          : (t[r] = o),
        t
      );
    }),
      (t.exports.__esModule = !0),
      (t.exports.default = t.exports);
  },
  function (t, r, o) {
    "use strict";
    var i = o(50),
      a = o(179),
      u = o(125),
      c = o(46),
      l = o(43).f,
      d = o(226),
      p = o(178),
      v = o(60),
      h = o(15),
      y = "Array Iterator",
      _ = c.set,
      g = c.getterFor(y);
    t.exports = d(
      Array,
      "Array",
      function (t, r) {
        _(this, {type: y, target: i(t), index: 0, kind: r});
      },
      function () {
        var t = g(this),
          r = t.target,
          o = t.index++;
        if (!r || o >= r.length) return (t.target = void 0), p(void 0, !0);
        switch (t.kind) {
          case "keys":
            return p(o, !1);
          case "values":
            return p(r[o], !1);
        }
        return p([o, r[o]], !1);
      },
      "values"
    );
    var b = (u.Arguments = u.Array);
    if ((a("keys"), a("values"), a("entries"), !v && h && "values" !== b.name))
      try {
        l(b, "name", {value: "values"});
      } catch (t) {}
  },
  function (t, r, o) {
    "use strict";
    var i = o(204).charAt,
      a = o(32),
      u = o(46),
      c = o(226),
      l = o(178),
      d = "String Iterator",
      p = u.set,
      v = u.getterFor(d);
    c(
      String,
      "String",
      function (t) {
        p(this, {type: d, string: a(t), index: 0});
      },
      function next() {
        var t,
          r = v(this),
          o = r.string,
          a = r.index;
        return a >= o.length
          ? l(void 0, !0)
          : ((t = i(o, a)), (r.index += t.length), l(t, !1));
      }
    );
  },
  function (t, r) {
    function _typeof(r) {
      return (
        (t.exports = _typeof =
          "function" == typeof Symbol && "symbol" == typeof Symbol.iterator
            ? function (t) {
                return typeof t;
              }
            : function (t) {
                return t &&
                  "function" == typeof Symbol &&
                  t.constructor === Symbol &&
                  t !== Symbol.prototype
                  ? "symbol"
                  : typeof t;
              }),
        (t.exports.__esModule = !0),
        (t.exports.default = t.exports),
        _typeof(r)
      );
    }
    (t.exports = _typeof), (t.exports.__esModule = !0), (t.exports.default = t.exports);
  },
  function (t, r, o) {
    "use strict";
    var i = o(5),
      a = o(6),
      u = o(50),
      c = o(94).f,
      l = o(15);
    i(
      {
        target: "Object",
        stat: !0,
        forced:
          !l ||
          a(function () {
            c(1);
          }),
        sham: !l,
      },
      {
        getOwnPropertyDescriptor: function getOwnPropertyDescriptor(t, r) {
          return c(u(t), r);
        },
      }
    );
  },
  function (t, r, o) {
    "use strict";
    (function (r) {
      var check = function (t) {
        return t && t.Math === Math && t;
      };
      t.exports =
        check("object" == typeof globalThis && globalThis) ||
        check("object" == typeof window && window) ||
        check("object" == typeof self && self) ||
        check("object" == typeof r && r) ||
        check("object" == typeof this && this) ||
        (function () {
          return this;
        })() ||
        Function("return this")();
    }).call(this, o(114));
  },
  function (t, r, o) {
    "use strict";
    var i = o(13),
      a = o(254),
      u = o(255),
      c = o(9),
      l = o(81),
      d = o(70),
      p = o(17)("iterator"),
      v = c.values,
      handlePrototype = function (t, r) {
        if (t) {
          if (t[p] !== v)
            try {
              l(t, p, v);
            } catch (r) {
              t[p] = v;
            }
          if ((d(t, r, !0), a[r]))
            for (var o in c)
              if (t[o] !== c[o])
                try {
                  l(t, o, c[o]);
                } catch (r) {
                  t[o] = c[o];
                }
        }
      };
    for (var h in a) handlePrototype(i[h] && i[h].prototype, h);
    handlePrototype(u, "DOMTokenList");
  },
  function (t, r, o) {
    "use strict";
    var i = o(6);
    t.exports = !i(function () {
      return (
        7 !==
        Object.defineProperty({}, 1, {
          get: function () {
            return 7;
          },
        })[1]
      );
    });
  },
  ,
  function (t, r, o) {
    "use strict";
    var i = o(13),
      a = o(105),
      u = o(31),
      c = o(149),
      l = o(104),
      d = o(246),
      p = i.Symbol,
      v = a("wks"),
      h = d ? p.for || p : (p && p.withoutSetter) || c;
    t.exports = function (t) {
      return u(v, t) || (v[t] = l && u(p, t) ? p[t] : h("Symbol." + t)), v[t];
    };
  },
  function (t, r, o) {
    "use strict";
    var i = o(13),
      a = o(254),
      u = o(255),
      c = o(334),
      l = o(81),
      handlePrototype = function (t) {
        if (t && t.forEach !== c)
          try {
            l(t, "forEach", c);
          } catch (r) {
            t.forEach = c;
          }
      };
    for (var d in a) a[d] && handlePrototype(i[d] && i[d].prototype);
    handlePrototype(u);
  },
  function (t, r, o) {
    "use strict";
    var i = "object" == typeof document && document.all;
    t.exports =
      void 0 === i && void 0 !== i
        ? function (t) {
            return "function" == typeof t || t === i;
          }
        : function (t) {
            return "function" == typeof t;
          };
  },
  ,
  function (t, r, o) {
    "use strict";
    var i = o(5),
      a = o(49),
      u = o(138);
    i(
      {
        target: "Object",
        stat: !0,
        forced: o(6)(function () {
          u(1);
        }),
      },
      {
        keys: function keys(t) {
          return u(a(t));
        },
      }
    );
  },
  function (t, r, o) {
    "use strict";
    o(342), o(344), o(345), o(86), o(347);
  },
  function (t, r, o) {
    "use strict";
    var i = o(147),
      a = Function.prototype.call;
    t.exports = i
      ? a.bind(a)
      : function () {
          return a.apply(a, arguments);
        };
  },
  function (t, r, o) {
    "use strict";
    var i = o(5),
      a = o(88).filter;
    i(
      {target: "Array", proto: !0, forced: !o(159)("filter")},
      {
        filter: function filter(t) {
          return a(this, t, arguments.length > 1 ? arguments[1] : void 0);
        },
      }
    );
  },
  function (t, r, o) {
    "use strict";
    var i = o(5),
      a = o(198);
    i({target: "RegExp", proto: !0, forced: /./.exec !== a}, {exec: a});
  },
  function (t, r, o) {
    var i = o(338),
      a = o(350),
      u = o(283),
      c = o(339);
    (t.exports = function _slicedToArray(t, r) {
      return i(t) || a(t, r) || u(t, r) || c();
    }),
      (t.exports.__esModule = !0),
      (t.exports.default = t.exports);
  },
  function (t, r, o) {
    "use strict";
    var i = o(5),
      a = o(88).map;
    i(
      {target: "Array", proto: !0, forced: !o(159)("map")},
      {
        map: function map(t) {
          return a(this, t, arguments.length > 1 ? arguments[1] : void 0);
        },
      }
    );
  },
  ,
  function (t, r, o) {
    "use strict";
    o(352);
  },
  function (t, r, o) {
    "use strict";
    var i = o(19);
    t.exports = function (t) {
      return "object" == typeof t ? null !== t : i(t);
    };
  },
  function (t, r, o) {
    "use strict";
    var i = o(7),
      a = o(49),
      u = i({}.hasOwnProperty);
    t.exports =
      Object.hasOwn ||
      function hasOwn(t, r) {
        return u(a(t), r);
      };
  },
  function (t, r, o) {
    "use strict";
    var i = o(109),
      a = String;
    t.exports = function (t) {
      if ("Symbol" === i(t))
        throw new TypeError("Cannot convert a Symbol value to a string");
      return a(t);
    };
  },
  function (t, r, o) {
    "use strict";
    var i = o(5),
      a = o(15),
      u = o(200).f;
    i(
      {target: "Object", stat: !0, forced: Object.defineProperties !== u, sham: !a},
      {defineProperties: u}
    );
  },
  function (t, r, o) {
    "use strict";
    var i = o(30),
      a = String,
      u = TypeError;
    t.exports = function (t) {
      if (i(t)) return t;
      throw new u(a(t) + " is not an object");
    };
  },
  function (t, r, o) {
    "use strict";
    var i = o(5),
      a = o(15),
      u = o(244),
      c = o(50),
      l = o(94),
      d = o(146);
    i(
      {target: "Object", stat: !0, sham: !a},
      {
        getOwnPropertyDescriptors: function getOwnPropertyDescriptors(t) {
          for (var r, o, i = c(t), a = l.f, p = u(i), v = {}, h = 0; p.length > h; )
            void 0 !== (o = a(i, (r = p[h++]))) && d(v, r, o);
          return v;
        },
      }
    );
  },
  ,
  function (t, r, o) {
    "use strict";
    var i = o(5),
      a = o(6),
      u = o(143),
      c = o(30),
      l = o(49),
      d = o(63),
      p = o(305),
      v = o(146),
      h = o(220),
      y = o(159),
      _ = o(17),
      g = o(113),
      b = _("isConcatSpreadable"),
      E =
        g >= 51 ||
        !a(function () {
          var t = [];
          return (t[b] = !1), t.concat()[0] !== t;
        }),
      isConcatSpreadable = function (t) {
        if (!c(t)) return !1;
        var r = t[b];
        return void 0 !== r ? !!r : u(t);
      };
    i(
      {target: "Array", proto: !0, arity: 1, forced: !E || !y("concat")},
      {
        concat: function concat(t) {
          var r,
            o,
            i,
            a,
            u,
            c = l(this),
            y = h(c, 0),
            _ = 0;
          for (r = -1, i = arguments.length; r < i; r++)
            if (isConcatSpreadable((u = -1 === r ? c : arguments[r])))
              for (a = d(u), p(_ + a), o = 0; o < a; o++, _++) o in u && v(y, _, u[o]);
            else p(_ + 1), v(y, _++, u);
          return (y.length = _), y;
        },
      }
    );
  },
  ,
  ,
  function (t, r, o) {
    "use strict";
    var i = o(19),
      a = o(43),
      u = o(240),
      c = o(196);
    t.exports = function (t, r, o, l) {
      l || (l = {});
      var d = l.enumerable,
        p = void 0 !== l.name ? l.name : r;
      if ((i(o) && u(o, p, l), l.global)) d ? (t[r] = o) : c(r, o);
      else {
        try {
          l.unsafe ? t[r] && (d = !0) : delete t[r];
        } catch (t) {}
        d
          ? (t[r] = o)
          : a.f(t, r, {
              value: o,
              enumerable: !1,
              configurable: !l.nonConfigurable,
              writable: !l.nonWritable,
            });
      }
      return t;
    };
  },
  ,
  ,
  function (t, r, o) {
    "use strict";
    var i = o(15),
      a = o(247),
      u = o(248),
      c = o(34),
      l = o(182),
      d = TypeError,
      p = Object.defineProperty,
      v = Object.getOwnPropertyDescriptor,
      h = "enumerable",
      y = "configurable",
      _ = "writable";
    r.f = i
      ? u
        ? function defineProperty(t, r, o) {
            if (
              (c(t),
              (r = l(r)),
              c(o),
              "function" == typeof t &&
                "prototype" === r &&
                "value" in o &&
                _ in o &&
                !o.writable)
            ) {
              var i = v(t, r);
              i &&
                i.writable &&
                ((t[r] = o.value),
                (o = {
                  configurable: y in o ? o.configurable : i.configurable,
                  enumerable: h in o ? o.enumerable : i.enumerable,
                  writable: !1,
                }));
            }
            return p(t, r, o);
          }
        : p
      : function defineProperty(t, r, o) {
          if ((c(t), (r = l(r)), c(o), a))
            try {
              return p(t, r, o);
            } catch (t) {}
          if ("get" in o || "set" in o) throw new d("Accessors not supported");
          return "value" in o && (t[r] = o.value), t;
        };
  },
  function (t, r, o) {
    "use strict";
    var i = o(15),
      a = o(136).EXISTS,
      u = o(7),
      c = o(73),
      l = Function.prototype,
      d = u(l.toString),
      p = /function\b(?:\s|\/\*[\S\s]*?\*\/|\/\/[^\n\r]*[\n\r]+)*([^\s(/]*)/,
      v = u(p.exec);
    i &&
      !a &&
      c(l, "name", {
        configurable: !0,
        get: function () {
          try {
            return v(p, d(this))[1];
          } catch (t) {
            return "";
          }
        },
      });
  },
  ,
  function (t, r, o) {
    "use strict";
    var i,
      a,
      u,
      c = o(249),
      l = o(13),
      d = o(30),
      p = o(81),
      v = o(31),
      h = o(195),
      y = o(160),
      _ = o(124),
      g = "Object already initialized",
      b = l.TypeError,
      E = l.WeakMap;
    if (c || h.state) {
      var m = h.state || (h.state = new E());
      (m.get = m.get),
        (m.has = m.has),
        (m.set = m.set),
        (i = function (t, r) {
          if (m.has(t)) throw new b(g);
          return (r.facade = t), m.set(t, r), r;
        }),
        (a = function (t) {
          return m.get(t) || {};
        }),
        (u = function (t) {
          return m.has(t);
        });
    } else {
      var w = y("state");
      (_[w] = !0),
        (i = function (t, r) {
          if (v(t, w)) throw new b(g);
          return (r.facade = t), p(t, w, r), r;
        }),
        (a = function (t) {
          return v(t, w) ? t[w] : {};
        }),
        (u = function (t) {
          return v(t, w);
        });
    }
    t.exports = {
      set: i,
      get: a,
      has: u,
      enforce: function (t) {
        return u(t) ? a(t) : i(t, {});
      },
      getterFor: function (t) {
        return function (r) {
          var o;
          if (!d(r) || (o = a(r)).type !== t)
            throw new b("Incompatible receiver, " + t + " required");
          return o;
        };
      },
    };
  },
  ,
  ,
  function (t, r, o) {
    "use strict";
    var i = o(56),
      a = Object;
    t.exports = function (t) {
      return a(i(t));
    };
  },
  function (t, r, o) {
    "use strict";
    var i = o(123),
      a = o(56);
    t.exports = function (t) {
      return i(a(t));
    };
  },
  function (t, r, o) {
    "use strict";
    var i = o(7),
      a = i({}.toString),
      u = i("".slice);
    t.exports = function (t) {
      return u(a(t), 8, -1);
    };
  },
  function (t, r, o) {
    "use strict";
    var i = o(5),
      a = o(143),
      u = o(166),
      c = o(30),
      l = o(203),
      d = o(63),
      p = o(50),
      v = o(146),
      h = o(17),
      y = o(159),
      _ = o(89),
      g = y("slice"),
      b = h("species"),
      E = Array,
      m = Math.max;
    i(
      {target: "Array", proto: !0, forced: !g},
      {
        slice: function slice(t, r) {
          var o,
            i,
            h,
            y = p(this),
            g = d(y),
            w = l(t, g),
            S = l(void 0 === r ? g : r, g);
          if (
            a(y) &&
            ((o = y.constructor),
            ((u(o) && (o === E || a(o.prototype))) || (c(o) && null === (o = o[b]))) &&
              (o = void 0),
            o === E || void 0 === o)
          )
            return _(y, w, S);
          for (i = new (void 0 === o ? E : o)(m(S - w, 0)), h = 0; w < S; w++, h++)
            w in y && v(i, h, y[w]);
          return (i.length = h), i;
        },
      }
    );
  },
  ,
  ,
  function (t, r, o) {
    "use strict";
    var i = o(136).PROPER,
      a = o(40),
      u = o(34),
      c = o(32),
      l = o(6),
      d = o(241),
      p = "toString",
      v = RegExp.prototype,
      h = v.toString,
      y = l(function () {
        return "/a/b" !== h.call({source: "a", flags: "b"});
      }),
      _ = i && h.name !== p;
    (y || _) &&
      a(
        v,
        p,
        function toString() {
          var t = u(this);
          return "/" + c(t.source) + "/" + c(d(t));
        },
        {unsafe: !0}
      );
  },
  function (t, r, o) {
    "use strict";
    var i = o(67),
      a = TypeError;
    t.exports = function (t) {
      if (i(t)) throw new a("Can't call method on " + t);
      return t;
    };
  },
  ,
  function (t, r, o) {
    "use strict";
    o(25);
    var i,
      a,
      u = o(5),
      c = o(23),
      l = o(19),
      d = o(34),
      p = o(32),
      v =
        ((i = !1),
        ((a = /[ac]/).exec = function () {
          return (i = !0), /./.exec.apply(this, arguments);
        }),
        !0 === a.test("abc") && i),
      h = /./.test;
    u(
      {target: "RegExp", proto: !0, forced: !v},
      {
        test: function (t) {
          var r = d(this),
            o = p(t),
            i = r.exec;
          if (!l(i)) return c(h, r, o);
          var a = c(i, r, o);
          return null !== a && (d(a), !0);
        },
      }
    );
  },
  ,
  function (t, r, o) {
    "use strict";
    t.exports = !1;
  },
  function (t, r, o) {
    "use strict";
    var i = o(13),
      a = o(19),
      aFunction = function (t) {
        return a(t) ? t : void 0;
      };
    t.exports = function (t, r) {
      return arguments.length < 2 ? aFunction(i[t]) : i[t] && i[t][r];
    };
  },
  ,
  function (t, r, o) {
    "use strict";
    var i = o(112);
    t.exports = function (t) {
      return i(t.length);
    };
  },
  function (t, r, o) {
    "use strict";
    var i = o(19),
      a = o(110),
      u = TypeError;
    t.exports = function (t) {
      if (i(t)) return t;
      throw new u(a(t) + " is not a function");
    };
  },
  ,
  function (t, r, o) {
    "use strict";
    var i = o(156),
      a = o(23),
      u = o(7),
      c = o(175),
      l = o(6),
      d = o(34),
      p = o(19),
      v = o(67),
      h = o(99),
      y = o(112),
      _ = o(32),
      g = o(56),
      b = o(212),
      E = o(98),
      m = o(337),
      w = o(174),
      S = o(17)("replace"),
      O = Math.max,
      x = Math.min,
      I = u([].concat),
      P = u([].push),
      T = u("".indexOf),
      A = u("".slice),
      R = "$0" === "a".replace(/./, "$0"),
      N = !!/./[S] && "" === /./[S]("a", "$0");
    c(
      "replace",
      function (t, r, o) {
        var u = N ? "$" : "$0";
        return [
          function replace(t, o) {
            var i = g(this),
              u = v(t) ? void 0 : E(t, S);
            return u ? a(u, t, i, o) : a(r, _(i), t, o);
          },
          function (t, a) {
            var c = d(this),
              l = _(t);
            if ("string" == typeof a && -1 === T(a, u) && -1 === T(a, "$<")) {
              var v = o(r, c, l, a);
              if (v.done) return v.value;
            }
            var g = p(a);
            g || (a = _(a));
            var E,
              S = c.global;
            S && ((E = c.unicode), (c.lastIndex = 0));
            for (var R, N = []; null !== (R = w(c, l)) && (P(N, R), S); ) {
              "" === _(R[0]) && (c.lastIndex = b(l, y(c.lastIndex), E));
            }
            for (var L, C = "", k = 0, M = 0; M < N.length; M++) {
              for (
                var j,
                  U = _((R = N[M])[0]),
                  W = O(x(h(R.index), l.length), 0),
                  D = [],
                  V = 1;
                V < R.length;
                V++
              )
                P(D, void 0 === (L = R[V]) ? L : String(L));
              var K = R.groups;
              if (g) {
                var B = I([U], D, W, l);
                void 0 !== K && P(B, K), (j = _(i(a, void 0, B)));
              } else j = m(U, l, W, D, K, a);
              W >= k && ((C += A(l, k, W) + j), (k = W + U.length));
            }
            return C + A(l, k);
          },
        ];
      },
      !!l(function () {
        var t = /./;
        return (
          (t.exec = function () {
            var t = [];
            return (t.groups = {a: "7"}), t;
          }),
          "7" !== "".replace(t, "$<a>")
        );
      }) ||
        !R ||
        N
    );
  },
  function (t, r, o) {
    "use strict";
    t.exports = function (t) {
      return null == t;
    };
  },
  ,
  ,
  function (t, r, o) {
    "use strict";
    var i = o(43).f,
      a = o(31),
      u = o(17)("toStringTag");
    t.exports = function (t, r, o) {
      t && !o && (t = t.prototype),
        t && !a(t, u) && i(t, u, {configurable: !0, value: r});
    };
  },
  ,
  ,
  function (t, r, o) {
    "use strict";
    var i = o(240),
      a = o(43);
    t.exports = function (t, r, o) {
      return (
        o.get && i(o.get, r, {getter: !0}),
        o.set && i(o.set, r, {setter: !0}),
        a.f(t, r, o)
      );
    };
  },
  ,
  function (t, r, o) {
    "use strict";
    var i = o(5),
      a = o(7),
      u = o(123),
      c = o(50),
      l = o(134),
      d = a([].join);
    i(
      {target: "Array", proto: !0, forced: u !== Object || !l("join", ",")},
      {
        join: function join(t) {
          return d(c(this), void 0 === t ? "," : t);
        },
      }
    );
  },
  ,
  ,
  function (t, r, o) {
    "use strict";
    var i = o(7);
    t.exports = i({}.isPrototypeOf);
  },
  function (t, r, o) {
    "use strict";
    var i = o(5),
      a = o(15),
      u = o(13),
      c = o(7),
      l = o(31),
      d = o(19),
      p = o(78),
      v = o(32),
      h = o(73),
      y = o(222),
      _ = u.Symbol,
      g = _ && _.prototype;
    if (a && d(_) && (!("description" in g) || void 0 !== _().description)) {
      var b = {},
        E = function Symbol() {
          var t =
              arguments.length < 1 || void 0 === arguments[0]
                ? void 0
                : v(arguments[0]),
            r = p(g, this) ? new _(t) : void 0 === t ? _() : _(t);
          return "" === t && (b[r] = !0), r;
        };
      y(E, _), (E.prototype = g), (g.constructor = E);
      var m = "Symbol(description detection)" === String(_("description detection")),
        w = c(g.valueOf),
        S = c(g.toString),
        O = /^Symbol\((.*)\)[^)]+$/,
        x = c("".replace),
        I = c("".slice);
      h(g, "description", {
        configurable: !0,
        get: function description() {
          var t = w(this);
          if (l(b, t)) return "";
          var r = S(t),
            o = m ? I(r, 7, -1) : x(r, O, "$1");
          return "" === o ? void 0 : o;
        },
      }),
        i({global: !0, constructor: !0, forced: !0}, {Symbol: E});
    }
  },
  ,
  function (t, r, o) {
    "use strict";
    var i = o(15),
      a = o(43),
      u = o(97);
    t.exports = i
      ? function (t, r, o) {
          return a.f(t, r, u(1, o));
        }
      : function (t, r, o) {
          return (t[r] = o), t;
        };
  },
  function (t, r, o) {
    "use strict";
    var i,
      a = o(34),
      u = o(200),
      c = o(197),
      l = o(124),
      d = o(269),
      p = o(167),
      v = o(160),
      h = v("IE_PROTO"),
      EmptyConstructor = function () {},
      scriptTag = function (t) {
        return "<script>" + t + "</" + "script>";
      },
      NullProtoObjectViaActiveX = function (t) {
        t.write(scriptTag("")), t.close();
        var r = t.parentWindow.Object;
        return (t = null), r;
      },
      NullProtoObject = function () {
        try {
          i = new ActiveXObject("htmlfile");
        } catch (t) {}
        var t, r;
        NullProtoObject =
          "undefined" != typeof document
            ? document.domain && i
              ? NullProtoObjectViaActiveX(i)
              : (((r = p("iframe")).style.display = "none"),
                d.appendChild(r),
                (r.src = String("javascript:")),
                (t = r.contentWindow.document).open(),
                t.write(scriptTag("document.F=Object")),
                t.close(),
                t.F)
            : NullProtoObjectViaActiveX(i);
        for (var o = c.length; o--; ) delete NullProtoObject.prototype[c[o]];
        return NullProtoObject();
      };
    (l[h] = !0),
      (t.exports =
        Object.create ||
        function create(t, r) {
          var o;
          return (
            null !== t
              ? ((EmptyConstructor.prototype = a(t)),
                (o = new EmptyConstructor()),
                (EmptyConstructor.prototype = null),
                (o[h] = t))
              : (o = NullProtoObject()),
            void 0 === r ? o : u.f(o, r)
          );
        });
  },
  ,
  ,
  ,
  function (t, r, o) {
    "use strict";
    var i = o(5),
      a = o(61),
      u = o(156),
      c = o(23),
      l = o(7),
      d = o(6),
      p = o(19),
      v = o(135),
      h = o(89),
      y = o(346),
      _ = o(104),
      g = String,
      b = a("JSON", "stringify"),
      E = l(/./.exec),
      m = l("".charAt),
      w = l("".charCodeAt),
      S = l("".replace),
      O = l((1).toString),
      x = /[\uD800-\uDFFF]/g,
      I = /^[\uD800-\uDBFF]$/,
      P = /^[\uDC00-\uDFFF]$/,
      T =
        !_ ||
        d(function () {
          var t = a("Symbol")("stringify detection");
          return "[null]" !== b([t]) || "{}" !== b({a: t}) || "{}" !== b(Object(t));
        }),
      A = d(function () {
        return '"\\udf06\\ud834"' !== b("\udf06\ud834") || '"\\udead"' !== b("\udead");
      }),
      stringifyWithSymbolsFix = function (t, r) {
        var o = h(arguments),
          i = y(r);
        if (p(i) || (void 0 !== t && !v(t)))
          return (
            (o[1] = function (t, r) {
              if ((p(i) && (r = c(i, this, g(t), r)), !v(r))) return r;
            }),
            u(b, null, o)
          );
      },
      fixIllFormed = function (t, r, o) {
        var i = m(o, r - 1),
          a = m(o, r + 1);
        return (E(I, t) && !E(P, a)) || (E(P, t) && !E(I, i))
          ? "\\u" + O(w(t, 0), 16)
          : t;
      };
    b &&
      i(
        {target: "JSON", stat: !0, arity: 3, forced: T || A},
        {
          stringify: function stringify(t, r, o) {
            var i = h(arguments),
              a = u(T ? stringifyWithSymbolsFix : b, null, i);
            return A && "string" == typeof a ? S(a, x, fixIllFormed) : a;
          },
        }
      );
  },
  function (t, r, o) {
    "use strict";
    var i = o(180),
      a = o(64),
      u = o(147),
      c = i(i.bind);
    t.exports = function (t, r) {
      return (
        a(t),
        void 0 === r
          ? t
          : u
          ? c(t, r)
          : function () {
              return t.apply(r, arguments);
            }
      );
    };
  },
  function (t, r, o) {
    "use strict";
    var i = o(87),
      a = o(7),
      u = o(123),
      c = o(49),
      l = o(63),
      d = o(220),
      p = a([].push),
      createMethod = function (t) {
        var r = 1 === t,
          o = 2 === t,
          a = 3 === t,
          v = 4 === t,
          h = 6 === t,
          y = 7 === t,
          _ = 5 === t || h;
        return function (g, b, E, m) {
          for (
            var w,
              S,
              O = c(g),
              x = u(O),
              I = l(x),
              P = i(b, E),
              T = 0,
              A = m || d,
              R = r ? A(g, I) : o || y ? A(g, 0) : void 0;
            I > T;
            T++
          )
            if ((_ || T in x) && ((S = P((w = x[T]), T, O)), t))
              if (r) R[T] = S;
              else if (S)
                switch (t) {
                  case 3:
                    return !0;
                  case 5:
                    return w;
                  case 6:
                    return T;
                  case 2:
                    p(R, w);
                }
              else
                switch (t) {
                  case 4:
                    return !1;
                  case 7:
                    p(R, w);
                }
          return h ? -1 : a || v ? v : R;
        };
      };
    t.exports = {
      forEach: createMethod(0),
      map: createMethod(1),
      filter: createMethod(2),
      some: createMethod(3),
      every: createMethod(4),
      find: createMethod(5),
      findIndex: createMethod(6),
      filterReject: createMethod(7),
    };
  },
  function (t, r, o) {
    "use strict";
    var i = o(7);
    t.exports = i([].slice);
  },
  ,
  ,
  ,
  function (t, r, o) {
    "use strict";
    o(217)("iterator");
  },
  function (t, r, o) {
    "use strict";
    var i = o(15),
      a = o(23),
      u = o(168),
      c = o(97),
      l = o(50),
      d = o(182),
      p = o(31),
      v = o(247),
      h = Object.getOwnPropertyDescriptor;
    r.f = i
      ? h
      : function getOwnPropertyDescriptor(t, r) {
          if (((t = l(t)), (r = d(r)), v))
            try {
              return h(t, r);
            } catch (t) {}
          if (p(t, r)) return c(!a(u.f, t, r), t[r]);
        };
  },
  function (t, r, o) {
    "use strict";
    var i = o(5),
      a = o(266);
    i(
      {
        target: "Array",
        stat: !0,
        forced: !o(194)(function (t) {
          Array.from(t);
        }),
      },
      {from: a}
    );
  },
  function (t, r, o) {
    "use strict";
    t.exports = ("undefined" != typeof navigator && String(navigator.userAgent)) || "";
  },
  function (t, r, o) {
    "use strict";
    t.exports = function (t, r) {
      return {
        enumerable: !(1 & t),
        configurable: !(2 & t),
        writable: !(4 & t),
        value: r,
      };
    };
  },
  function (t, r, o) {
    "use strict";
    var i = o(64),
      a = o(67);
    t.exports = function (t, r) {
      var o = t[r];
      return a(o) ? void 0 : i(o);
    };
  },
  function (t, r, o) {
    "use strict";
    var i = o(333);
    t.exports = function (t) {
      var r = +t;
      return r != r || 0 === r ? 0 : i(r);
    };
  },
  function (t, r, o) {
    "use strict";
    o(1), o(3), o(18), o(21), Object.defineProperty(r, "__esModule", {value: !0});
    var i = {
      API_VERSIONS: !0,
      EXTERNAL_ENVIRONMENTS_API_V1: !0,
      INTERNAL_ENVIRONMENTS_API_V1: !0,
      EXTERNAL_ENVIRONMENTS_API_V2: !0,
      VERSION: !0,
      INTERNAL_ENVIRONMENTS_API_V2: !0,
      ENVIRONMENTS_TO_DOMAIN: !0,
      PLAID_WEBVIEW_NAMESPACE: !0,
      PAYMENT_INITIATION: !0,
      PRODUCTS_API_V1: !0,
      PRODUCTS_API_V2_ONLY: !0,
      PRODUCTS_API_V2: !0,
      PRODUCTS_API_V2_BETA: !0,
      I18N_SUPPORTED_LANGUAGES: !0,
      DEFAULT_LANGUAGE: !0,
      FLEXIBLE_INPUT_OVERWRITE_STATUSES: !0,
      CLOUDFLARE_ETH_MAINNET_URL: !0,
      MAINNET_HEX_CHAIN_ID: !0,
      PLAID_LINK_BUTTON_ID: !0,
      PLAID_FLOW_INTERNAL_NAMESPACE: !0,
      PLAID_INTERNAL_NAMESPACE: !0,
      CREATE_PARAMETERS: !0,
    };
    (r.CLOUDFLARE_ETH_MAINNET_URL = r.API_VERSIONS = void 0),
      Object.defineProperty(r, "CREATE_PARAMETERS", {
        enumerable: !0,
        get: function get() {
          return a.CREATE_PARAMETERS;
        },
      }),
      (r.PLAID_FLOW_INTERNAL_NAMESPACE =
        r.PAYMENT_INITIATION =
        r.MAINNET_HEX_CHAIN_ID =
        r.INTERNAL_ENVIRONMENTS_API_V2 =
        r.INTERNAL_ENVIRONMENTS_API_V1 =
        r.I18N_SUPPORTED_LANGUAGES =
        r.FLEXIBLE_INPUT_OVERWRITE_STATUSES =
        r.EXTERNAL_ENVIRONMENTS_API_V2 =
        r.EXTERNAL_ENVIRONMENTS_API_V1 =
        r.ENVIRONMENTS_TO_DOMAIN =
        r.DEFAULT_LANGUAGE =
          void 0),
      Object.defineProperty(r, "PLAID_INTERNAL_NAMESPACE", {
        enumerable: !0,
        get: function get() {
          return a.PLAID_INTERNAL_NAMESPACE;
        },
      }),
      (r.VERSION =
        r.PRODUCTS_API_V2_ONLY =
        r.PRODUCTS_API_V2_BETA =
        r.PRODUCTS_API_V2 =
        r.PRODUCTS_API_V1 =
        r.PLAID_WEBVIEW_NAMESPACE =
        r.PLAID_LINK_BUTTON_ID =
          void 0);
    var a = o(231);
    Object.keys(a).forEach(function (t) {
      "default" !== t &&
        "__esModule" !== t &&
        (Object.prototype.hasOwnProperty.call(i, t) ||
          (t in r && r[t] === a[t]) ||
          Object.defineProperty(r, t, {
            enumerable: !0,
            get: function get() {
              return a[t];
            },
          }));
    });
    r.API_VERSIONS = ["v1", "v2"];
    r.EXTERNAL_ENVIRONMENTS_API_V1 = ["tartan", "production"];
    r.INTERNAL_ENVIRONMENTS_API_V1 = ["testing", "tartan", "production"];
    r.EXTERNAL_ENVIRONMENTS_API_V2 = ["sandbox", "development", "production"];
    var u = String("2.0.1951");
    r.VERSION = u;
    r.INTERNAL_ENVIRONMENTS_API_V2 = [
      "end2end",
      "devenv",
      "testing",
      "sandbox",
      "development",
      "production",
    ];
    r.ENVIRONMENTS_TO_DOMAIN = {
      devenv: "http://localhost:8082",
      testing: "https://api-v2-testing.plaid.com",
      tartan: "https://development.plaid.com",
      development: "https://development.plaid.com",
      sandbox: "https://sandbox.plaid.com",
      production: "https://production.plaid.com",
    };
    r.PLAID_WEBVIEW_NAMESPACE = "plaidlink";
    var c = "payment_initiation";
    r.PAYMENT_INITIATION = c;
    r.PRODUCTS_API_V1 = ["auth", "connect", "income", "info"];
    var l = [
      "account_verify",
      "assets",
      "bank_transfer",
      "transfer",
      "ddta",
      "deposit_switch",
      "holdings",
      "income_verification",
      "investments_auth",
      "investments",
      "liabilities",
      c,
      "sba_verification",
      "liabilities_report",
    ];
    r.PRODUCTS_API_V2_ONLY = l;
    var d = [
      "account_verify",
      "assets",
      "auth",
      "transfer",
      "bank_transfer",
      "ddta",
      "deposit_switch",
      "holdings",
      "identity",
      "income",
      "income_verification",
      "investments_auth",
      "investments",
      "liabilities",
      c,
      "transactions",
      "sba_verification",
      "liabilities_report",
    ];
    r.PRODUCTS_API_V2 = d;
    var p = [
      "account_verify",
      "bank_transfer",
      "transfer",
      "holdings",
      "investments_auth",
      "ddta",
      c,
      "deposit_switch",
      "sba_verification",
      "liabilities_report",
      "income_verification",
    ];
    r.PRODUCTS_API_V2_BETA = p;
    r.I18N_SUPPORTED_LANGUAGES = ["en", "es", "fr"];
    r.DEFAULT_LANGUAGE = "en";
    r.FLEXIBLE_INPUT_OVERWRITE_STATUSES = ["choose_device"];
    r.CLOUDFLARE_ETH_MAINNET_URL = "https://cloudflare-eth.com/v1/mainnet";
    r.MAINNET_HEX_CHAIN_ID = "0x1";
    r.PLAID_LINK_BUTTON_ID = "plaid-link-button";
    r.PLAID_FLOW_INTERNAL_NAMESPACE = "plaid_flow";
  },
  ,
  ,
  ,
  function (t, r, o) {
    "use strict";
    var i = o(113),
      a = o(6),
      u = o(13).String;
    t.exports =
      !!Object.getOwnPropertySymbols &&
      !a(function () {
        var t = Symbol("symbol detection");
        return !u(t) || !(Object(t) instanceof Symbol) || (!Symbol.sham && i && i < 41);
      });
  },
  function (t, r, o) {
    "use strict";
    var i = o(195);
    t.exports = function (t, r) {
      return i[t] || (i[t] = r || {});
    };
  },
  ,
  ,
  function (t, r, o) {
    "use strict";
    o(267);
  },
  function (t, r, o) {
    "use strict";
    var i = o(199),
      a = o(19),
      u = o(51),
      c = o(17)("toStringTag"),
      l = Object,
      d =
        "Arguments" ===
        u(
          (function () {
            return arguments;
          })()
        );
    t.exports = i
      ? u
      : function (t) {
          var r, o, i;
          return void 0 === t
            ? "Undefined"
            : null === t
            ? "Null"
            : "string" ==
              typeof (o = (function (t, r) {
                try {
                  return t[r];
                } catch (t) {}
              })((r = l(t)), c))
            ? o
            : d
            ? u(r)
            : "Object" === (i = u(r)) && a(r.callee)
            ? "Arguments"
            : i;
        };
  },
  function (t, r, o) {
    "use strict";
    var i = String;
    t.exports = function (t) {
      try {
        return i(t);
      } catch (t) {
        return "Object";
      }
    };
  },
  function (t, r, o) {
    "use strict";
    var i = o(250),
      a = o(197).concat("length", "prototype");
    r.f =
      Object.getOwnPropertyNames ||
      function getOwnPropertyNames(t) {
        return i(t, a);
      };
  },
  function (t, r, o) {
    "use strict";
    var i = o(99),
      a = Math.min;
    t.exports = function (t) {
      var r = i(t);
      return r > 0 ? a(r, 9007199254740991) : 0;
    };
  },
  function (t, r, o) {
    "use strict";
    var i,
      a,
      u = o(13),
      c = o(96),
      l = u.process,
      d = u.Deno,
      p = (l && l.versions) || (d && d.version),
      v = p && p.v8;
    v && (a = (i = v.split("."))[0] > 0 && i[0] < 4 ? 1 : +(i[0] + i[1])),
      !a &&
        c &&
        (!(i = c.match(/Edge\/(\d+)/)) || i[1] >= 74) &&
        (i = c.match(/Chrome\/(\d+)/)) &&
        (a = +i[1]),
      (t.exports = a);
  },
  function (t, r) {
    var o;
    o = (function () {
      return this;
    })();
    try {
      o = o || new Function("return this")();
    } catch (t) {
      "object" == typeof window && (o = window);
    }
    t.exports = o;
  },
  function (t, r, o) {
    "use strict";
    var i = o(78),
      a = TypeError;
    t.exports = function (t, r) {
      if (i(r, t)) return t;
      throw new a("Incorrect invocation");
    };
  },
  ,
  ,
  function (t, r, o) {
    "use strict";
    var i = o(5),
      a = o(180),
      u = o(177).indexOf,
      c = o(134),
      l = a([].indexOf),
      d = !!l && 1 / l([1], 1, -0) < 0;
    i(
      {target: "Array", proto: !0, forced: d || !c("indexOf")},
      {
        indexOf: function indexOf(t) {
          var r = arguments.length > 1 ? arguments[1] : void 0;
          return d ? l(this, t, r) || 0 : u(this, t, r);
        },
      }
    );
  },
  ,
  function (t, r, o) {
    "use strict";
    var i = o(5),
      a = o(324).left,
      u = o(134),
      c = o(113);
    i(
      {
        target: "Array",
        proto: !0,
        forced: (!o(163) && c > 79 && c < 83) || !u("reduce"),
      },
      {
        reduce: function reduce(t) {
          var r = arguments.length;
          return a(this, t, r, r > 1 ? arguments[1] : void 0);
        },
      }
    );
  },
  function (t, r, o) {
    "use strict";
    var i = o(5),
      a = o(355).entries;
    i(
      {target: "Object", stat: !0},
      {
        entries: function entries(t) {
          return a(t);
        },
      }
    );
  },
  ,
  function (t, r, o) {
    "use strict";
    var i = o(7),
      a = o(6),
      u = o(51),
      c = Object,
      l = i("".split);
    t.exports = a(function () {
      return !c("z").propertyIsEnumerable(0);
    })
      ? function (t) {
          return "String" === u(t) ? l(t, "") : c(t);
        }
      : c;
  },
  function (t, r, o) {
    "use strict";
    t.exports = {};
  },
  function (t, r, o) {
    "use strict";
    t.exports = {};
  },
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  function (t, r, o) {
    "use strict";
    var i = o(6);
    t.exports = function (t, r) {
      var o = [][t];
      return (
        !!o &&
        i(function () {
          o.call(
            null,
            r ||
              function () {
                return 1;
              },
            1
          );
        })
      );
    };
  },
  function (t, r, o) {
    "use strict";
    var i = o(61),
      a = o(19),
      u = o(78),
      c = o(246),
      l = Object;
    t.exports = c
      ? function (t) {
          return "symbol" == typeof t;
        }
      : function (t) {
          var r = i("Symbol");
          return a(r) && u(r.prototype, l(t));
        };
  },
  function (t, r, o) {
    "use strict";
    var i = o(15),
      a = o(31),
      u = Function.prototype,
      c = i && Object.getOwnPropertyDescriptor,
      l = a(u, "name"),
      d = l && "something" === function something() {}.name,
      p = l && (!i || (i && c(u, "name").configurable));
    t.exports = {EXISTS: l, PROPER: d, CONFIGURABLE: p};
  },
  ,
  function (t, r, o) {
    "use strict";
    var i = o(250),
      a = o(197);
    t.exports =
      Object.keys ||
      function keys(t) {
        return i(t, a);
      };
  },
  ,
  ,
  ,
  function (t, r, o) {
    "use strict";
    var i = o(87),
      a = o(23),
      u = o(34),
      c = o(110),
      l = o(230),
      d = o(63),
      p = o(78),
      v = o(183),
      h = o(150),
      y = o(256),
      _ = TypeError,
      Result = function (t, r) {
        (this.stopped = t), (this.result = r);
      },
      g = Result.prototype;
    t.exports = function (t, r, o) {
      var b,
        E,
        m,
        w,
        S,
        O,
        x,
        I = o && o.that,
        P = !(!o || !o.AS_ENTRIES),
        T = !(!o || !o.IS_RECORD),
        A = !(!o || !o.IS_ITERATOR),
        R = !(!o || !o.INTERRUPTED),
        N = i(r, I),
        stop = function (t) {
          return b && y(b, "normal", t), new Result(!0, t);
        },
        callFn = function (t) {
          return P
            ? (u(t), R ? N(t[0], t[1], stop) : N(t[0], t[1]))
            : R
            ? N(t, stop)
            : N(t);
        };
      if (T) b = t.iterator;
      else if (A) b = t;
      else {
        if (!(E = h(t))) throw new _(c(t) + " is not iterable");
        if (l(E)) {
          for (m = 0, w = d(t); w > m; m++) if ((S = callFn(t[m])) && p(g, S)) return S;
          return new Result(!1);
        }
        b = v(t, E);
      }
      for (O = T ? t.next : b.next; !(x = a(O, b)).done; ) {
        try {
          S = callFn(x.value);
        } catch (t) {
          y(b, "throw", t);
        }
        if ("object" == typeof S && S && p(g, S)) return S;
      }
      return new Result(!1);
    };
  },
  function (t, r, o) {
    "use strict";
    var i = o(51);
    t.exports =
      Array.isArray ||
      function isArray(t) {
        return "Array" === i(t);
      };
  },
  function (t, r, o) {
    "use strict";
    var i = o(6),
      a = o(19),
      u = /#|\.prototype\./,
      isForced = function (t, r) {
        var o = l[c(t)];
        return o === p || (o !== d && (a(r) ? i(r) : !!r));
      },
      c = (isForced.normalize = function (t) {
        return String(t).replace(u, ".").toLowerCase();
      }),
      l = (isForced.data = {}),
      d = (isForced.NATIVE = "N"),
      p = (isForced.POLYFILL = "P");
    t.exports = isForced;
  },
  ,
  function (t, r, o) {
    "use strict";
    var i = o(15),
      a = o(43),
      u = o(97);
    t.exports = function (t, r, o) {
      i ? a.f(t, r, u(0, o)) : (t[r] = o);
    };
  },
  function (t, r, o) {
    "use strict";
    var i = o(6);
    t.exports = !i(function () {
      var t = function () {}.bind();
      return "function" != typeof t || t.hasOwnProperty("prototype");
    });
  },
  ,
  function (t, r, o) {
    "use strict";
    var i = o(7),
      a = 0,
      u = Math.random(),
      c = i((1).toString);
    t.exports = function (t) {
      return "Symbol(" + (void 0 === t ? "" : t) + ")_" + c(++a + u, 36);
    };
  },
  function (t, r, o) {
    "use strict";
    var i = o(109),
      a = o(98),
      u = o(67),
      c = o(125),
      l = o(17)("iterator");
    t.exports = function (t) {
      if (!u(t)) return a(t, l) || a(t, "@@iterator") || c[i(t)];
    };
  },
  ,
  function (t, r, o) {
    "use strict";
    var i = o(15),
      a = o(13),
      u = o(7),
      c = o(144),
      l = o(193),
      d = o(81),
      p = o(82),
      v = o(111).f,
      h = o(78),
      y = o(263),
      _ = o(32),
      g = o(241),
      b = o(169),
      E = o(340),
      m = o(40),
      w = o(6),
      S = o(31),
      O = o(46).enforce,
      x = o(218),
      I = o(17),
      P = o(201),
      T = o(251),
      A = I("match"),
      R = a.RegExp,
      N = R.prototype,
      L = a.SyntaxError,
      C = u(N.exec),
      k = u("".charAt),
      M = u("".replace),
      j = u("".indexOf),
      U = u("".slice),
      W = /^\?<[^\s\d!#%&*+<=>@^][^\s!#%&*+<=>@^]*>/,
      D = /a/g,
      V = /a/g,
      K = new R(D) !== D,
      B = b.MISSED_STICKY,
      H = b.UNSUPPORTED_Y,
      q =
        i &&
        (!K ||
          B ||
          P ||
          T ||
          w(function () {
            return (
              (V[A] = !1), R(D) !== D || R(V) === V || "/a/i" !== String(R(D, "i"))
            );
          }));
    if (c("RegExp", q)) {
      for (
        var z = function RegExp(t, r) {
            var o,
              i,
              a,
              u,
              c,
              v,
              b = h(N, this),
              E = y(t),
              m = void 0 === r,
              w = [],
              x = t;
            if (!b && E && m && t.constructor === z) return t;
            if (
              ((E || h(N, t)) && ((t = t.source), m && (r = g(x))),
              (t = void 0 === t ? "" : _(t)),
              (r = void 0 === r ? "" : _(r)),
              (x = t),
              P &&
                ("dotAll" in D) &&
                (i = !!r && j(r, "s") > -1) &&
                (r = M(r, /s/g, "")),
              (o = r),
              B &&
                ("sticky" in D) &&
                (a = !!r && j(r, "y") > -1) &&
                H &&
                (r = M(r, /y/g, "")),
              T &&
                ((u = (function (t) {
                  for (
                    var r,
                      o = t.length,
                      i = 0,
                      a = "",
                      u = [],
                      c = p(null),
                      l = !1,
                      d = !1,
                      v = 0,
                      h = "";
                    i <= o;
                    i++
                  ) {
                    if ("\\" === (r = k(t, i))) r += k(t, ++i);
                    else if ("]" === r) l = !1;
                    else if (!l)
                      switch (!0) {
                        case "[" === r:
                          l = !0;
                          break;
                        case "(" === r:
                          C(W, U(t, i + 1)) && ((i += 2), (d = !0)), (a += r), v++;
                          continue;
                        case ">" === r && d:
                          if ("" === h || S(c, h))
                            throw new L("Invalid capture group name");
                          (c[h] = !0), (u[u.length] = [h, v]), (d = !1), (h = "");
                          continue;
                      }
                    d ? (h += r) : (a += r);
                  }
                  return [a, u];
                })(t)),
                (t = u[0]),
                (w = u[1])),
              (c = l(R(t, r), b ? this : N, z)),
              (i || a || w.length) &&
                ((v = O(c)),
                i &&
                  ((v.dotAll = !0),
                  (v.raw = z(
                    (function (t) {
                      for (var r, o = t.length, i = 0, a = "", u = !1; i <= o; i++)
                        "\\" !== (r = k(t, i))
                          ? u || "." !== r
                            ? ("[" === r ? (u = !0) : "]" === r && (u = !1), (a += r))
                            : (a += "[\\s\\S]")
                          : (a += r + k(t, ++i));
                      return a;
                    })(t),
                    o
                  ))),
                a && (v.sticky = !0),
                w.length && (v.groups = w)),
              t !== x)
            )
              try {
                d(c, "source", "" === x ? "(?:)" : x);
              } catch (t) {}
            return c;
          },
          G = v(R),
          Q = 0;
        G.length > Q;

      )
        E(z, R, G[Q++]);
      (N.constructor = z), (z.prototype = N), m(a, "RegExp", z, {constructor: !0});
    }
    x("RegExp");
  },
  function (t, r, o) {
    "use strict";
    var i = o(15),
      a = o(201),
      u = o(51),
      c = o(73),
      l = o(46).get,
      d = RegExp.prototype,
      p = TypeError;
    i &&
      a &&
      c(d, "dotAll", {
        configurable: !0,
        get: function dotAll() {
          if (this !== d) {
            if ("RegExp" === u(this)) return !!l(this).dotAll;
            throw new p("Incompatible receiver, RegExp required");
          }
        },
      });
  },
  function (t, r, o) {
    "use strict";
    var i = o(15),
      a = o(169).MISSED_STICKY,
      u = o(51),
      c = o(73),
      l = o(46).get,
      d = RegExp.prototype,
      p = TypeError;
    i &&
      a &&
      c(d, "sticky", {
        configurable: !0,
        get: function sticky() {
          if (this !== d) {
            if ("RegExp" === u(this)) return !!l(this).sticky;
            throw new p("Incompatible receiver, RegExp required");
          }
        },
      });
  },
  ,
  function (t, r, o) {
    "use strict";
    var i = o(147),
      a = Function.prototype,
      u = a.apply,
      c = a.call;
    t.exports =
      ("object" == typeof Reflect && Reflect.apply) ||
      (i
        ? c.bind(u)
        : function () {
            return c.apply(u, arguments);
          });
  },
  ,
  ,
  function (t, r, o) {
    "use strict";
    var i = o(6),
      a = o(17),
      u = o(113),
      c = a("species");
    t.exports = function (t) {
      return (
        u >= 51 ||
        !i(function () {
          var r = [];
          return (
            ((r.constructor = {})[c] = function () {
              return {foo: 1};
            }),
            1 !== r[t](Boolean).foo
          );
        })
      );
    };
  },
  function (t, r, o) {
    "use strict";
    var i = o(105),
      a = o(149),
      u = i("keys");
    t.exports = function (t) {
      return u[t] || (u[t] = a(t));
    };
  },
  function (t, r, o) {
    "use strict";
    r.f = Object.getOwnPropertySymbols;
  },
  ,
  function (t, r, o) {
    "use strict";
    var i = o(13),
      a = o(51);
    t.exports = "process" === a(i.process);
  },
  function (t, r, o) {
    "use strict";
    var i = o(329),
      a = o(30),
      u = o(56),
      c = o(335);
    t.exports =
      Object.setPrototypeOf ||
      ("__proto__" in {}
        ? (function () {
            var t,
              r = !1,
              o = {};
            try {
              (t = i(Object.prototype, "__proto__", "set"))(o, []),
                (r = o instanceof Array);
            } catch (t) {}
            return function setPrototypeOf(o, i) {
              return u(o), c(i), a(o) ? (r ? t(o, i) : (o.__proto__ = i), o) : o;
            };
          })()
        : void 0);
  },
  ,
  function (t, r, o) {
    "use strict";
    var i = o(7),
      a = o(6),
      u = o(19),
      c = o(109),
      l = o(61),
      d = o(208),
      noop = function () {},
      p = l("Reflect", "construct"),
      v = /^\s*(?:class|function)\b/,
      h = i(v.exec),
      y = !v.test(noop),
      _ = function isConstructor(t) {
        if (!u(t)) return !1;
        try {
          return p(noop, [], t), !0;
        } catch (t) {
          return !1;
        }
      },
      g = function isConstructor(t) {
        if (!u(t)) return !1;
        switch (c(t)) {
          case "AsyncFunction":
          case "GeneratorFunction":
          case "AsyncGeneratorFunction":
            return !1;
        }
        try {
          return y || !!h(v, d(t));
        } catch (t) {
          return !0;
        }
      };
    (g.sham = !0),
      (t.exports =
        !p ||
        a(function () {
          var t;
          return (
            _(_.call) ||
            !_(Object) ||
            !_(function () {
              t = !0;
            }) ||
            t
          );
        })
          ? g
          : _);
  },
  function (t, r, o) {
    "use strict";
    var i = o(13),
      a = o(30),
      u = i.document,
      c = a(u) && a(u.createElement);
    t.exports = function (t) {
      return c ? u.createElement(t) : {};
    };
  },
  function (t, r, o) {
    "use strict";
    var i = {}.propertyIsEnumerable,
      a = Object.getOwnPropertyDescriptor,
      u = a && !i.call({1: 2}, 1);
    r.f = u
      ? function propertyIsEnumerable(t) {
          var r = a(this, t);
          return !!r && r.enumerable;
        }
      : i;
  },
  function (t, r, o) {
    "use strict";
    var i = o(6),
      a = o(13).RegExp,
      u = i(function () {
        var t = a("a", "y");
        return (t.lastIndex = 2), null !== t.exec("abcd");
      }),
      c =
        u ||
        i(function () {
          return !a("a", "y").sticky;
        }),
      l =
        u ||
        i(function () {
          var t = a("^r", "gy");
          return (t.lastIndex = 2), null !== t.exec("str");
        });
    t.exports = {BROKEN_CARET: l, MISSED_STICKY: c, UNSUPPORTED_Y: u};
  },
  function (t, r, o) {
    "use strict";
    var i = o(31),
      a = o(19),
      u = o(49),
      c = o(160),
      l = o(307),
      d = c("IE_PROTO"),
      p = Object,
      v = p.prototype;
    t.exports = l
      ? p.getPrototypeOf
      : function (t) {
          var r = u(t);
          if (i(r, d)) return r[d];
          var o = r.constructor;
          return a(o) && r instanceof o ? o.prototype : r instanceof p ? v : null;
        };
  },
  function (t, r, o) {
    "use strict";
    var i = o(5),
      a = o(7),
      u = o(124),
      c = o(30),
      l = o(31),
      d = o(43).f,
      p = o(111),
      v = o(224),
      h = o(330),
      y = o(149),
      _ = o(221),
      g = !1,
      b = y("meta"),
      E = 0,
      setMetadata = function (t) {
        d(t, b, {value: {objectID: "O" + E++, weakData: {}}});
      },
      m = (t.exports = {
        enable: function () {
          (m.enable = function () {}), (g = !0);
          var t = p.f,
            r = a([].splice),
            o = {};
          (o[b] = 1),
            t(o).length &&
              ((p.f = function (o) {
                for (var i = t(o), a = 0, u = i.length; a < u; a++)
                  if (i[a] === b) {
                    r(i, a, 1);
                    break;
                  }
                return i;
              }),
              i({target: "Object", stat: !0, forced: !0}, {getOwnPropertyNames: v.f}));
        },
        fastKey: function (t, r) {
          if (!c(t))
            return "symbol" == typeof t ? t : ("string" == typeof t ? "S" : "P") + t;
          if (!l(t, b)) {
            if (!h(t)) return "F";
            if (!r) return "E";
            setMetadata(t);
          }
          return t[b].objectID;
        },
        getWeakData: function (t, r) {
          if (!l(t, b)) {
            if (!h(t)) return !0;
            if (!r) return !1;
            setMetadata(t);
          }
          return t[b].weakData;
        },
        onFreeze: function (t) {
          return _ && g && h(t) && !l(t, b) && setMetadata(t), t;
        },
      });
    u[b] = !0;
  },
  function (t, r, o) {
    "use strict";
    var i = o(40);
    t.exports = function (t, r, o) {
      for (var a in r) i(t, a, r[a], o);
      return t;
    };
  },
  ,
  function (t, r, o) {
    "use strict";
    var i = o(23),
      a = o(34),
      u = o(19),
      c = o(51),
      l = o(198),
      d = TypeError;
    t.exports = function (t, r) {
      var o = t.exec;
      if (u(o)) {
        var p = i(o, t, r);
        return null !== p && a(p), p;
      }
      if ("RegExp" === c(t)) return i(l, t, r);
      throw new d("RegExp#exec called on incompatible receiver");
    };
  },
  function (t, r, o) {
    "use strict";
    o(25);
    var i = o(23),
      a = o(40),
      u = o(198),
      c = o(6),
      l = o(17),
      d = o(81),
      p = l("species"),
      v = RegExp.prototype;
    t.exports = function (t, r, o, h) {
      var y = l(t),
        _ = !c(function () {
          var r = {};
          return (
            (r[y] = function () {
              return 7;
            }),
            7 !== ""[t](r)
          );
        }),
        g =
          _ &&
          !c(function () {
            var r = !1,
              o = /a/;
            return (
              "split" === t &&
                (((o = {}).constructor = {}),
                (o.constructor[p] = function () {
                  return o;
                }),
                (o.flags = ""),
                (o[y] = /./[y])),
              (o.exec = function () {
                return (r = !0), null;
              }),
              o[y](""),
              !r
            );
          });
      if (!_ || !g || o) {
        var b = /./[y],
          E = r(y, ""[t], function (t, r, o, a, c) {
            var l = r.exec;
            return l === u || l === v.exec
              ? _ && !c
                ? {done: !0, value: i(b, r, o, a)}
                : {done: !0, value: i(t, o, r, a)}
              : {done: !1};
          });
        a(String.prototype, t, E[0]), a(v, y, E[1]);
      }
      h && d(v[y], "sham", !0);
    };
  },
  ,
  function (t, r, o) {
    "use strict";
    var i = o(50),
      a = o(203),
      u = o(63),
      createMethod = function (t) {
        return function (r, o, c) {
          var l = i(r),
            d = u(l);
          if (0 === d) return !t && -1;
          var p,
            v = a(c, d);
          if (t && o != o) {
            for (; d > v; ) if ((p = l[v++]) != p) return !0;
          } else for (; d > v; v++) if ((t || v in l) && l[v] === o) return t || v || 0;
          return !t && -1;
        };
      };
    t.exports = {includes: createMethod(!0), indexOf: createMethod(!1)};
  },
  function (t, r, o) {
    "use strict";
    t.exports = function (t, r) {
      return {value: t, done: r};
    };
  },
  function (t, r, o) {
    "use strict";
    var i = o(17),
      a = o(82),
      u = o(43).f,
      c = i("unscopables"),
      l = Array.prototype;
    void 0 === l[c] && u(l, c, {configurable: !0, value: a(null)}),
      (t.exports = function (t) {
        l[c][t] = !0;
      });
  },
  function (t, r, o) {
    "use strict";
    var i = o(51),
      a = o(7);
    t.exports = function (t) {
      if ("Function" === i(t)) return a(t);
    };
  },
  ,
  function (t, r, o) {
    "use strict";
    var i = o(268),
      a = o(135);
    t.exports = function (t) {
      var r = i(t, "string");
      return a(r) ? r : r + "";
    };
  },
  function (t, r, o) {
    "use strict";
    var i = o(23),
      a = o(64),
      u = o(34),
      c = o(110),
      l = o(150),
      d = TypeError;
    t.exports = function (t, r) {
      var o = arguments.length < 2 ? l(t) : r;
      if (a(o)) return u(i(o, t));
      throw new d(c(t) + " is not iterable");
    };
  },
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  function (t, r, o) {
    "use strict";
    var i = TypeError;
    t.exports = function (t, r) {
      if (t < r) throw new i("Not enough arguments");
      return t;
    };
  },
  function (t, r, o) {
    "use strict";
    var i = o(19),
      a = o(30),
      u = o(164);
    t.exports = function (t, r, o) {
      var c, l;
      return (
        u &&
          i((c = r.constructor)) &&
          c !== o &&
          a((l = c.prototype)) &&
          l !== o.prototype &&
          u(t, l),
        t
      );
    };
  },
  function (t, r, o) {
    "use strict";
    var i = o(17)("iterator"),
      a = !1;
    try {
      var u = 0,
        c = {
          next: function () {
            return {done: !!u++};
          },
          return: function () {
            a = !0;
          },
        };
      (c[i] = function () {
        return this;
      }),
        Array.from(c, function () {
          throw 2;
        });
    } catch (t) {}
    t.exports = function (t, r) {
      try {
        if (!r && !a) return !1;
      } catch (t) {
        return !1;
      }
      var o = !1;
      try {
        var u = {};
        (u[i] = function () {
          return {
            next: function () {
              return {done: (o = !0)};
            },
          };
        }),
          t(u);
      } catch (t) {}
      return o;
    };
  },
  function (t, r, o) {
    "use strict";
    var i = o(60),
      a = o(13),
      u = o(196),
      c = "__core-js_shared__",
      l = (t.exports = a[c] || u(c, {}));
    (l.versions || (l.versions = [])).push({
      version: "3.36.1",
      mode: i ? "pure" : "global",
      copyright: "© 2014-2024 Denis Pushkarev (zloirock.ru)",
      license: "https://github.com/zloirock/core-js/blob/v3.36.1/LICENSE",
      source: "https://github.com/zloirock/core-js",
    });
  },
  function (t, r, o) {
    "use strict";
    var i = o(13),
      a = Object.defineProperty;
    t.exports = function (t, r) {
      try {
        a(i, t, {value: r, configurable: !0, writable: !0});
      } catch (o) {
        i[t] = r;
      }
      return r;
    };
  },
  function (t, r, o) {
    "use strict";
    t.exports = [
      "constructor",
      "hasOwnProperty",
      "isPrototypeOf",
      "propertyIsEnumerable",
      "toLocaleString",
      "toString",
      "valueOf",
    ];
  },
  function (t, r, o) {
    "use strict";
    var i,
      a,
      u = o(23),
      c = o(7),
      l = o(32),
      d = o(242),
      p = o(169),
      v = o(105),
      h = o(82),
      y = o(46).get,
      _ = o(201),
      g = o(251),
      b = v("native-string-replace", String.prototype.replace),
      E = RegExp.prototype.exec,
      m = E,
      w = c("".charAt),
      S = c("".indexOf),
      O = c("".replace),
      x = c("".slice),
      I =
        ((a = /b*/g),
        u(E, (i = /a/), "a"),
        u(E, a, "a"),
        0 !== i.lastIndex || 0 !== a.lastIndex),
      P = p.BROKEN_CARET,
      T = void 0 !== /()??/.exec("")[1];
    (I || T || P || _ || g) &&
      (m = function exec(t) {
        var r,
          o,
          i,
          a,
          c,
          p,
          v,
          _ = this,
          g = y(_),
          A = l(t),
          R = g.raw;
        if (R)
          return (
            (R.lastIndex = _.lastIndex),
            (r = u(m, R, A)),
            (_.lastIndex = R.lastIndex),
            r
          );
        var N = g.groups,
          L = P && _.sticky,
          C = u(d, _),
          k = _.source,
          M = 0,
          j = A;
        if (
          (L &&
            ((C = O(C, "y", "")),
            -1 === S(C, "g") && (C += "g"),
            (j = x(A, _.lastIndex)),
            _.lastIndex > 0 &&
              (!_.multiline || (_.multiline && "\n" !== w(A, _.lastIndex - 1))) &&
              ((k = "(?: " + k + ")"), (j = " " + j), M++),
            (o = new RegExp("^(?:" + k + ")", C))),
          T && (o = new RegExp("^" + k + "$(?!\\s)", C)),
          I && (i = _.lastIndex),
          (a = u(E, L ? o : _, j)),
          L
            ? a
              ? ((a.input = x(a.input, M)),
                (a[0] = x(a[0], M)),
                (a.index = _.lastIndex),
                (_.lastIndex += a[0].length))
              : (_.lastIndex = 0)
            : I && a && (_.lastIndex = _.global ? a.index + a[0].length : i),
          T &&
            a &&
            a.length > 1 &&
            u(b, a[0], o, function () {
              for (c = 1; c < arguments.length - 2; c++)
                void 0 === arguments[c] && (a[c] = void 0);
            }),
          a && N)
        )
          for (a.groups = p = h(null), c = 0; c < N.length; c++)
            p[(v = N[c])[0]] = a[v[1]];
        return a;
      }),
      (t.exports = m);
  },
  function (t, r, o) {
    "use strict";
    var i = {};
    (i[o(17)("toStringTag")] = "z"), (t.exports = "[object z]" === String(i));
  },
  function (t, r, o) {
    "use strict";
    var i = o(15),
      a = o(248),
      u = o(43),
      c = o(34),
      l = o(50),
      d = o(138);
    r.f =
      i && !a
        ? Object.defineProperties
        : function defineProperties(t, r) {
            c(t);
            for (var o, i = l(r), a = d(r), p = a.length, v = 0; p > v; )
              u.f(t, (o = a[v++]), i[o]);
            return t;
          };
  },
  function (t, r, o) {
    "use strict";
    var i = o(6),
      a = o(13).RegExp;
    t.exports = i(function () {
      var t = a(".", "s");
      return !(t.dotAll && t.test("\n") && "s" === t.flags);
    });
  },
  ,
  function (t, r, o) {
    "use strict";
    var i = o(99),
      a = Math.max,
      u = Math.min;
    t.exports = function (t, r) {
      var o = i(t);
      return o < 0 ? a(o + r, 0) : u(o, r);
    };
  },
  function (t, r, o) {
    "use strict";
    var i = o(7),
      a = o(99),
      u = o(32),
      c = o(56),
      l = i("".charAt),
      d = i("".charCodeAt),
      p = i("".slice),
      createMethod = function (t) {
        return function (r, o) {
          var i,
            v,
            h = u(c(r)),
            y = a(o),
            _ = h.length;
          return y < 0 || y >= _
            ? t
              ? ""
              : void 0
            : (i = d(h, y)) < 55296 ||
              i > 56319 ||
              y + 1 === _ ||
              (v = d(h, y + 1)) < 56320 ||
              v > 57343
            ? t
              ? l(h, y)
              : i
            : t
            ? p(h, y, y + 2)
            : v - 56320 + ((i - 55296) << 10) + 65536;
        };
      };
    t.exports = {codeAt: createMethod(!1), charAt: createMethod(!0)};
  },
  ,
  ,
  ,
  function (t, r, o) {
    "use strict";
    var i = o(7),
      a = o(19),
      u = o(195),
      c = i(Function.toString);
    a(u.inspectSource) ||
      (u.inspectSource = function (t) {
        return c(t);
      }),
      (t.exports = u.inspectSource);
  },
  ,
  function (t, r, o) {
    "use strict";
    var i = o(5),
      a = o(7),
      u = o(64),
      c = o(49),
      l = o(63),
      d = o(364),
      p = o(32),
      v = o(6),
      h = o(243),
      y = o(134),
      _ = o(369),
      g = o(370),
      b = o(113),
      E = o(366),
      m = [],
      w = a(m.sort),
      S = a(m.push),
      O = v(function () {
        m.sort(void 0);
      }),
      x = v(function () {
        m.sort(null);
      }),
      I = y("sort"),
      P = !v(function () {
        if (b) return b < 70;
        if (!(_ && _ > 3)) {
          if (g) return !0;
          if (E) return E < 603;
          var t,
            r,
            o,
            i,
            a = "";
          for (t = 65; t < 76; t++) {
            switch (((r = String.fromCharCode(t)), t)) {
              case 66:
              case 69:
              case 70:
              case 72:
                o = 3;
                break;
              case 68:
              case 71:
                o = 4;
                break;
              default:
                o = 2;
            }
            for (i = 0; i < 47; i++) m.push({k: r + i, v: o});
          }
          for (
            m.sort(function (t, r) {
              return r.v - t.v;
            }),
              i = 0;
            i < m.length;
            i++
          )
            (r = m[i].k.charAt(0)), a.charAt(a.length - 1) !== r && (a += r);
          return "DGBEFHACIJK" !== a;
        }
      });
    i(
      {target: "Array", proto: !0, forced: O || !x || !I || !P},
      {
        sort: function sort(t) {
          void 0 !== t && u(t);
          var r = c(this);
          if (P) return void 0 === t ? w(r) : w(r, t);
          var o,
            i,
            a = [],
            v = l(r);
          for (i = 0; i < v; i++) i in r && S(a, r[i]);
          for (
            h(
              a,
              (function (t) {
                return function (r, o) {
                  return void 0 === o
                    ? -1
                    : void 0 === r
                    ? 1
                    : void 0 !== t
                    ? +t(r, o) || 0
                    : p(r) > p(o)
                    ? 1
                    : -1;
                };
              })(t)
            ),
              o = l(a),
              i = 0;
            i < o;

          )
            r[i] = a[i++];
          for (; i < v; ) d(r, i++);
          return r;
        },
      }
    );
  },
  ,
  function (t, r, o) {
    "use strict";
    var i = o(204).charAt;
    t.exports = function (t, r, o) {
      return r + (o ? i(t, r).length : 1);
    };
  },
  ,
  ,
  ,
  ,
  function (t, r, o) {
    "use strict";
    var i = o(273),
      a = o(31),
      u = o(252),
      c = o(43).f;
    t.exports = function (t) {
      var r = i.Symbol || (i.Symbol = {});
      a(r, t) || c(r, t, {value: u.f(t)});
    };
  },
  function (t, r, o) {
    "use strict";
    var i = o(61),
      a = o(73),
      u = o(17),
      c = o(15),
      l = u("species");
    t.exports = function (t) {
      var r = i(t);
      c &&
        r &&
        !r[l] &&
        a(r, l, {
          configurable: !0,
          get: function () {
            return this;
          },
        });
    };
  },
  ,
  function (t, r, o) {
    "use strict";
    var i = o(343);
    t.exports = function (t, r) {
      return new (i(t))(0 === r ? 0 : r);
    };
  },
  function (t, r, o) {
    "use strict";
    var i = o(6);
    t.exports = !i(function () {
      return Object.isExtensible(Object.preventExtensions({}));
    });
  },
  function (t, r, o) {
    "use strict";
    var i = o(31),
      a = o(244),
      u = o(94),
      c = o(43);
    t.exports = function (t, r, o) {
      for (var l = a(r), d = c.f, p = u.f, v = 0; v < l.length; v++) {
        var h = l[v];
        i(t, h) || (o && i(o, h)) || d(t, h, p(r, h));
      }
    };
  },
  function (t, r, o) {
    "use strict";
    o(1),
      Object.defineProperty(r, "__esModule", {value: !0}),
      (r.default = void 0),
      o(25),
      o(66),
      o(3),
      o(55);
    var i = function uuid() {
      var t = window.crypto || window.msCrypto;
      return null != t && "randomUUID" in t
        ? t.randomUUID()
        : "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (t) {
            var r = (16 * Math.random()) | 0;
            return ("x" === t ? r : (3 & r) | 8).toString(16);
          });
    };
    r.default = i;
  },
  function (t, r, o) {
    "use strict";
    var i = o(51),
      a = o(50),
      u = o(111).f,
      c = o(89),
      l =
        "object" == typeof window && window && Object.getOwnPropertyNames
          ? Object.getOwnPropertyNames(window)
          : [];
    t.exports.f = function getOwnPropertyNames(t) {
      return l && "Window" === i(t)
        ? (function (t) {
            try {
              return u(t);
            } catch (t) {
              return c(l);
            }
          })(t)
        : u(a(t));
    };
  },
  ,
  function (t, r, o) {
    "use strict";
    var i = o(5),
      a = o(23),
      u = o(60),
      c = o(136),
      l = o(19),
      d = o(245),
      p = o(170),
      v = o(164),
      h = o(70),
      y = o(81),
      _ = o(40),
      g = o(17),
      b = o(125),
      E = o(257),
      m = c.PROPER,
      w = c.CONFIGURABLE,
      S = E.IteratorPrototype,
      O = E.BUGGY_SAFARI_ITERATORS,
      x = g("iterator"),
      I = "keys",
      P = "values",
      T = "entries",
      returnThis = function () {
        return this;
      };
    t.exports = function (t, r, o, c, g, E, A) {
      d(o, r, c);
      var R,
        N,
        L,
        getIterationMethod = function (t) {
          if (t === g && U) return U;
          if (!O && t && t in M) return M[t];
          switch (t) {
            case I:
              return function keys() {
                return new o(this, t);
              };
            case P:
              return function values() {
                return new o(this, t);
              };
            case T:
              return function entries() {
                return new o(this, t);
              };
          }
          return function () {
            return new o(this);
          };
        },
        C = r + " Iterator",
        k = !1,
        M = t.prototype,
        j = M[x] || M["@@iterator"] || (g && M[g]),
        U = (!O && j) || getIterationMethod(g),
        W = ("Array" === r && M.entries) || j;
      if (
        (W &&
          (R = p(W.call(new t()))) !== Object.prototype &&
          R.next &&
          (u || p(R) === S || (v ? v(R, S) : l(R[x]) || _(R, x, returnThis)),
          h(R, C, !0, !0),
          u && (b[C] = returnThis)),
        m &&
          g === P &&
          j &&
          j.name !== P &&
          (!u && w
            ? y(M, "name", P)
            : ((k = !0),
              (U = function values() {
                return a(j, this);
              }))),
        g)
      )
        if (
          ((N = {
            values: getIterationMethod(P),
            keys: E ? U : getIterationMethod(I),
            entries: getIterationMethod(T),
          }),
          A)
        )
          for (L in N) (O || k || !(L in M)) && _(M, L, N[L]);
        else i({target: r, proto: !0, forced: O || k}, N);
      return (u && !A) || M[x] === U || _(M, x, U, {name: g}), (b[r] = U), N;
    };
  },
  ,
  ,
  ,
  function (t, r, o) {
    "use strict";
    var i = o(17),
      a = o(125),
      u = i("iterator"),
      c = Array.prototype;
    t.exports = function (t) {
      return void 0 !== t && (a.Array === t || c[u] === t);
    };
  },
  function (t, r, o) {
    "use strict";
    (function (t) {
      o(1),
        Object.defineProperty(r, "__esModule", {value: !0}),
        (r.PLAID_INTERNAL_NAMESPACE =
          r.LINK_WEB_SDK_VERSION =
          r.LINK_OPEN_HTML_PATH =
          r.LINK_IFRAME_SANDBOX_PERMISSIONS =
          r.LINK_IFRAME_FEATURE_POLICY_URLS =
          r.LINK_HTML_PATH =
          r.LINK_CLIENT_URL =
          r.LINK_CLIENT_STABLE_URL =
          r.LINK_CLIENT_CORS_ORIGIN =
          r.CREATE_PARAMETERS =
            void 0),
        o(75);
      var i = String("https://cdn.plaid.com/link/2.0.1951");
      r.LINK_CLIENT_URL = i;
      var a = String("https://cdn.plaid.com/link/v2/stable");
      r.LINK_CLIENT_STABLE_URL = a;
      r.LINK_HTML_PATH = "/link.html";
      r.LINK_OPEN_HTML_PATH = "/link-open.html";
      r.PLAID_INTERNAL_NAMESPACE = "plaid_link";
      r.CREATE_PARAMETERS = [
        "env",
        "onEvent",
        "onExit",
        "onLoad",
        "onSuccess",
        "receivedRedirectUri",
        "token",
      ];
      var u = String("https://cdn.plaid.com");
      r.LINK_CLIENT_CORS_ORIGIN = u;
      var c = t.env.LINK_WEB_SDK_VERSION;
      r.LINK_WEB_SDK_VERSION = c;
      var l = [
        "https://cdn-testing.plaid.com",
        "https://cdn.plaid.com",
        "https://secure.plaid.com",
        "https://secure-testing.plaid.com",
        "https://verify.plaid.com",
        "https://verify-sandbox.plaid.com",
        "https://verify-testing.plaid.com",
      ].join(" ");
      r.LINK_IFRAME_FEATURE_POLICY_URLS = l;
      r.LINK_IFRAME_SANDBOX_PERMISSIONS =
        "allow-downloads allow-forms allow-modals allow-popups allow-popups-to-escape-sandbox allow-same-origin allow-scripts allow-top-navigation";
    }).call(this, o(234));
  },
  ,
  ,
  function (t, r) {
    var o,
      i,
      a = (t.exports = {});
    function defaultSetTimout() {
      throw new Error("setTimeout has not been defined");
    }
    function defaultClearTimeout() {
      throw new Error("clearTimeout has not been defined");
    }
    function runTimeout(t) {
      if (o === setTimeout) return setTimeout(t, 0);
      if ((o === defaultSetTimout || !o) && setTimeout)
        return (o = setTimeout), setTimeout(t, 0);
      try {
        return o(t, 0);
      } catch (r) {
        try {
          return o.call(null, t, 0);
        } catch (r) {
          return o.call(this, t, 0);
        }
      }
    }
    !(function () {
      try {
        o = "function" == typeof setTimeout ? setTimeout : defaultSetTimout;
      } catch (t) {
        o = defaultSetTimout;
      }
      try {
        i = "function" == typeof clearTimeout ? clearTimeout : defaultClearTimeout;
      } catch (t) {
        i = defaultClearTimeout;
      }
    })();
    var u,
      c = [],
      l = !1,
      d = -1;
    function cleanUpNextTick() {
      l &&
        u &&
        ((l = !1), u.length ? (c = u.concat(c)) : (d = -1), c.length && drainQueue());
    }
    function drainQueue() {
      if (!l) {
        var t = runTimeout(cleanUpNextTick);
        l = !0;
        for (var r = c.length; r; ) {
          for (u = c, c = []; ++d < r; ) u && u[d].run();
          (d = -1), (r = c.length);
        }
        (u = null),
          (l = !1),
          (function runClearTimeout(t) {
            if (i === clearTimeout) return clearTimeout(t);
            if ((i === defaultClearTimeout || !i) && clearTimeout)
              return (i = clearTimeout), clearTimeout(t);
            try {
              return i(t);
            } catch (r) {
              try {
                return i.call(null, t);
              } catch (r) {
                return i.call(this, t);
              }
            }
          })(t);
      }
    }
    function Item(t, r) {
      (this.fun = t), (this.array = r);
    }
    function noop() {}
    (a.nextTick = function (t) {
      var r = new Array(arguments.length - 1);
      if (arguments.length > 1)
        for (var o = 1; o < arguments.length; o++) r[o - 1] = arguments[o];
      c.push(new Item(t, r)), 1 !== c.length || l || runTimeout(drainQueue);
    }),
      (Item.prototype.run = function () {
        this.fun.apply(null, this.array);
      }),
      (a.title = "browser"),
      (a.browser = !0),
      (a.env = {}),
      (a.argv = []),
      (a.version = ""),
      (a.versions = {}),
      (a.on = noop),
      (a.addListener = noop),
      (a.once = noop),
      (a.off = noop),
      (a.removeListener = noop),
      (a.removeAllListeners = noop),
      (a.emit = noop),
      (a.prependListener = noop),
      (a.prependOnceListener = noop),
      (a.listeners = function (t) {
        return [];
      }),
      (a.binding = function (t) {
        throw new Error("process.binding is not supported");
      }),
      (a.cwd = function () {
        return "/";
      }),
      (a.chdir = function (t) {
        throw new Error("process.chdir is not supported");
      }),
      (a.umask = function () {
        return 0;
      });
  },
  function (t, r, o) {
    "use strict";
    var i = o(5),
      a = o(274);
    i({target: "Object", stat: !0, arity: 2, forced: Object.assign !== a}, {assign: a});
  },
  ,
  ,
  ,
  ,
  function (t, r, o) {
    "use strict";
    var i = o(7),
      a = o(6),
      u = o(19),
      c = o(31),
      l = o(15),
      d = o(136).CONFIGURABLE,
      p = o(208),
      v = o(46),
      h = v.enforce,
      y = v.get,
      _ = String,
      g = Object.defineProperty,
      b = i("".slice),
      E = i("".replace),
      m = i([].join),
      w =
        l &&
        !a(function () {
          return 8 !== g(function () {}, "length", {value: 8}).length;
        }),
      S = String(String).split("String"),
      O = (t.exports = function (t, r, o) {
        "Symbol(" === b(_(r), 0, 7) &&
          (r = "[" + E(_(r), /^Symbol\(([^)]*)\).*$/, "$1") + "]"),
          o && o.getter && (r = "get " + r),
          o && o.setter && (r = "set " + r),
          (!c(t, "name") || (d && t.name !== r)) &&
            (l ? g(t, "name", {value: r, configurable: !0}) : (t.name = r)),
          w &&
            o &&
            c(o, "arity") &&
            t.length !== o.arity &&
            g(t, "length", {value: o.arity});
        try {
          o && c(o, "constructor") && o.constructor
            ? l && g(t, "prototype", {writable: !1})
            : t.prototype && (t.prototype = void 0);
        } catch (t) {}
        var i = h(t);
        return c(i, "source") || (i.source = m(S, "string" == typeof r ? r : "")), t;
      });
    Function.prototype.toString = O(function toString() {
      return (u(this) && y(this).source) || p(this);
    }, "toString");
  },
  function (t, r, o) {
    "use strict";
    var i = o(23),
      a = o(31),
      u = o(78),
      c = o(242),
      l = RegExp.prototype;
    t.exports = function (t) {
      var r = t.flags;
      return void 0 !== r || "flags" in l || a(t, "flags") || !u(l, t) ? r : i(c, t);
    };
  },
  function (t, r, o) {
    "use strict";
    var i = o(34);
    t.exports = function () {
      var t = i(this),
        r = "";
      return (
        t.hasIndices && (r += "d"),
        t.global && (r += "g"),
        t.ignoreCase && (r += "i"),
        t.multiline && (r += "m"),
        t.dotAll && (r += "s"),
        t.unicode && (r += "u"),
        t.unicodeSets && (r += "v"),
        t.sticky && (r += "y"),
        r
      );
    };
  },
  function (t, r, o) {
    "use strict";
    var i = o(89),
      a = Math.floor,
      sort = function (t, r) {
        var o = t.length;
        if (o < 8)
          for (var u, c, l = 1; l < o; ) {
            for (c = l, u = t[l]; c && r(t[c - 1], u) > 0; ) t[c] = t[--c];
            c !== l++ && (t[c] = u);
          }
        else
          for (
            var d = a(o / 2),
              p = sort(i(t, 0, d), r),
              v = sort(i(t, d), r),
              h = p.length,
              y = v.length,
              _ = 0,
              g = 0;
            _ < h || g < y;

          )
            t[_ + g] =
              _ < h && g < y
                ? r(p[_], v[g]) <= 0
                  ? p[_++]
                  : v[g++]
                : _ < h
                ? p[_++]
                : v[g++];
        return t;
      };
    t.exports = sort;
  },
  function (t, r, o) {
    "use strict";
    var i = o(61),
      a = o(7),
      u = o(111),
      c = o(161),
      l = o(34),
      d = a([].concat);
    t.exports =
      i("Reflect", "ownKeys") ||
      function ownKeys(t) {
        var r = u.f(l(t)),
          o = c.f;
        return o ? d(r, o(t)) : r;
      };
  },
  function (t, r, o) {
    "use strict";
    var i = o(257).IteratorPrototype,
      a = o(82),
      u = o(97),
      c = o(70),
      l = o(125),
      returnThis = function () {
        return this;
      };
    t.exports = function (t, r, o, d) {
      var p = r + " Iterator";
      return (
        (t.prototype = a(i, {next: u(+!d, o)})), c(t, p, !1, !0), (l[p] = returnThis), t
      );
    };
  },
  function (t, r, o) {
    "use strict";
    var i = o(104);
    t.exports = i && !Symbol.sham && "symbol" == typeof Symbol.iterator;
  },
  function (t, r, o) {
    "use strict";
    var i = o(15),
      a = o(6),
      u = o(167);
    t.exports =
      !i &&
      !a(function () {
        return (
          7 !==
          Object.defineProperty(u("div"), "a", {
            get: function () {
              return 7;
            },
          }).a
        );
      });
  },
  function (t, r, o) {
    "use strict";
    var i = o(15),
      a = o(6);
    t.exports =
      i &&
      a(function () {
        return (
          42 !==
          Object.defineProperty(function () {}, "prototype", {value: 42, writable: !1})
            .prototype
        );
      });
  },
  function (t, r, o) {
    "use strict";
    var i = o(13),
      a = o(19),
      u = i.WeakMap;
    t.exports = a(u) && /native code/.test(String(u));
  },
  function (t, r, o) {
    "use strict";
    var i = o(7),
      a = o(31),
      u = o(50),
      c = o(177).indexOf,
      l = o(124),
      d = i([].push);
    t.exports = function (t, r) {
      var o,
        i = u(t),
        p = 0,
        v = [];
      for (o in i) !a(l, o) && a(i, o) && d(v, o);
      for (; r.length > p; ) a(i, (o = r[p++])) && (~c(v, o) || d(v, o));
      return v;
    };
  },
  function (t, r, o) {
    "use strict";
    var i = o(6),
      a = o(13).RegExp;
    t.exports = i(function () {
      var t = a("(?<a>b)", "g");
      return "b" !== t.exec("b").groups.a || "bc" !== "b".replace(t, "$<a>c");
    });
  },
  function (t, r, o) {
    "use strict";
    var i = o(17);
    r.f = i;
  },
  function (t, r, o) {
    "use strict";
    var i = o(104);
    t.exports = i && !!Symbol.for && !!Symbol.keyFor;
  },
  function (t, r, o) {
    "use strict";
    t.exports = {
      CSSRuleList: 0,
      CSSStyleDeclaration: 0,
      CSSValueList: 0,
      ClientRectList: 0,
      DOMRectList: 0,
      DOMStringList: 0,
      DOMTokenList: 1,
      DataTransferItemList: 0,
      FileList: 0,
      HTMLAllCollection: 0,
      HTMLCollection: 0,
      HTMLFormElement: 0,
      HTMLSelectElement: 0,
      MediaList: 0,
      MimeTypeArray: 0,
      NamedNodeMap: 0,
      NodeList: 1,
      PaintRequestList: 0,
      Plugin: 0,
      PluginArray: 0,
      SVGLengthList: 0,
      SVGNumberList: 0,
      SVGPathSegList: 0,
      SVGPointList: 0,
      SVGStringList: 0,
      SVGTransformList: 0,
      SourceBufferList: 0,
      StyleSheetList: 0,
      TextTrackCueList: 0,
      TextTrackList: 0,
      TouchList: 0,
    };
  },
  function (t, r, o) {
    "use strict";
    var i = o(167)("span").classList,
      a = i && i.constructor && i.constructor.prototype;
    t.exports = a === Object.prototype ? void 0 : a;
  },
  function (t, r, o) {
    "use strict";
    var i = o(23),
      a = o(34),
      u = o(98);
    t.exports = function (t, r, o) {
      var c, l;
      a(t);
      try {
        if (!(c = u(t, "return"))) {
          if ("throw" === r) throw o;
          return o;
        }
        c = i(c, t);
      } catch (t) {
        (l = !0), (c = t);
      }
      if ("throw" === r) throw o;
      if (l) throw c;
      return a(c), o;
    };
  },
  function (t, r, o) {
    "use strict";
    var i,
      a,
      u,
      c = o(6),
      l = o(19),
      d = o(30),
      p = o(82),
      v = o(170),
      h = o(40),
      y = o(17),
      _ = o(60),
      g = y("iterator"),
      b = !1;
    [].keys &&
      ("next" in (u = [].keys())
        ? (a = v(v(u))) !== Object.prototype && (i = a)
        : (b = !0)),
      !d(i) ||
      c(function () {
        var t = {};
        return i[g].call(t) !== t;
      })
        ? (i = {})
        : _ && (i = p(i)),
      l(i[g]) ||
        h(i, g, function () {
          return this;
        }),
      (t.exports = {IteratorPrototype: i, BUGGY_SAFARI_ITERATORS: b});
  },
  ,
  ,
  ,
  ,
  ,
  function (t, r, o) {
    "use strict";
    var i = o(30),
      a = o(51),
      u = o(17)("match");
    t.exports = function (t) {
      var r;
      return i(t) && (void 0 !== (r = t[u]) ? !!r : "RegExp" === a(t));
    };
  },
  ,
  function (t, r, o) {
    "use strict";
    var i = o(6),
      a = o(17),
      u = o(15),
      c = o(60),
      l = a("iterator");
    t.exports = !i(function () {
      var t = new URL("b?a=1&b=2&c=3", "http://a"),
        r = t.searchParams,
        o = new URLSearchParams("a=1&a=2&b=3"),
        i = "";
      return (
        (t.pathname = "c%20d"),
        r.forEach(function (t, o) {
          r.delete("b"), (i += o + t);
        }),
        o.delete("a", 2),
        o.delete("b", void 0),
        (c &&
          (!t.toJSON ||
            !o.has("a", 1) ||
            o.has("a", 2) ||
            !o.has("a", void 0) ||
            o.has("b"))) ||
          (!r.size && (c || !u)) ||
          !r.sort ||
          "http://a/c%20d?a=1&c=3" !== t.href ||
          "3" !== r.get("c") ||
          "a=1" !== String(new URLSearchParams("?a=1")) ||
          !r[l] ||
          "a" !== new URL("https://a@b").username ||
          "b" !== new URLSearchParams(new URLSearchParams("a=b")).get("a") ||
          "xn--e1aybc" !== new URL("http://тест").host ||
          "#%D0%B1" !== new URL("http://a#б").hash ||
          "a1c3" !== i ||
          "x" !== new URL("http://x", void 0).host
      );
    });
  },
  function (t, r, o) {
    "use strict";
    var i = o(87),
      a = o(23),
      u = o(49),
      c = o(348),
      l = o(230),
      d = o(166),
      p = o(63),
      v = o(146),
      h = o(183),
      y = o(150),
      _ = Array;
    t.exports = function from(t) {
      var r = u(t),
        o = d(this),
        g = arguments.length,
        b = g > 1 ? arguments[1] : void 0,
        E = void 0 !== b;
      E && (b = i(b, g > 2 ? arguments[2] : void 0));
      var m,
        w,
        S,
        O,
        x,
        I,
        P = y(r),
        T = 0;
      if (!P || (this === _ && l(P)))
        for (m = p(r), w = o ? new this(m) : _(m); m > T; T++)
          (I = E ? b(r[T], T) : r[T]), v(w, T, I);
      else
        for (w = o ? new this() : [], x = (O = h(r, P)).next; !(S = a(x, O)).done; T++)
          (I = E ? c(O, b, [S.value, T], !0) : S.value), v(w, T, I);
      return (w.length = T), w;
    };
  },
  function (t, r, o) {
    "use strict";
    o(9);
    var i = o(5),
      a = o(13),
      u = o(270),
      c = o(23),
      l = o(7),
      d = o(15),
      p = o(265),
      v = o(40),
      h = o(73),
      y = o(172),
      _ = o(70),
      g = o(245),
      b = o(46),
      E = o(115),
      m = o(19),
      w = o(31),
      S = o(87),
      O = o(109),
      x = o(34),
      I = o(30),
      P = o(32),
      T = o(82),
      A = o(97),
      R = o(183),
      N = o(150),
      L = o(178),
      C = o(192),
      k = o(17),
      M = o(243),
      j = k("iterator"),
      U = "URLSearchParams",
      W = "URLSearchParamsIterator",
      D = b.set,
      V = b.getterFor(U),
      K = b.getterFor(W),
      B = u("fetch"),
      H = u("Request"),
      q = u("Headers"),
      z = H && H.prototype,
      G = q && q.prototype,
      Q = a.RegExp,
      X = a.TypeError,
      Y = a.decodeURIComponent,
      J = a.encodeURIComponent,
      $ = l("".charAt),
      Z = l([].join),
      ee = l([].push),
      te = l("".replace),
      ne = l([].shift),
      re = l([].splice),
      oe = l("".split),
      ie = l("".slice),
      ae = /\+/g,
      ue = Array(4),
      percentSequence = function (t) {
        return ue[t - 1] || (ue[t - 1] = Q("((?:%[\\da-f]{2}){" + t + "})", "gi"));
      },
      percentDecode = function (t) {
        try {
          return Y(t);
        } catch (r) {
          return t;
        }
      },
      deserialize = function (t) {
        var r = te(t, ae, " "),
          o = 4;
        try {
          return Y(r);
        } catch (t) {
          for (; o; ) r = te(r, percentSequence(o--), percentDecode);
          return r;
        }
      },
      ce = /[!'()~]|%20/g,
      se = {"!": "%21", "'": "%27", "(": "%28", ")": "%29", "~": "%7E", "%20": "+"},
      replacer = function (t) {
        return se[t];
      },
      serialize = function (t) {
        return te(J(t), ce, replacer);
      },
      fe = g(
        function Iterator(t, r) {
          D(this, {type: W, target: V(t).entries, index: 0, kind: r});
        },
        U,
        function next() {
          var t = K(this),
            r = t.target,
            o = t.index++;
          if (!r || o >= r.length) return (t.target = void 0), L(void 0, !0);
          var i = r[o];
          switch (t.kind) {
            case "keys":
              return L(i.key, !1);
            case "values":
              return L(i.value, !1);
          }
          return L([i.key, i.value], !1);
        },
        !0
      ),
      URLSearchParamsState = function (t) {
        (this.entries = []),
          (this.url = null),
          void 0 !== t &&
            (I(t)
              ? this.parseObject(t)
              : this.parseQuery(
                  "string" == typeof t ? ("?" === $(t, 0) ? ie(t, 1) : t) : P(t)
                ));
      };
    URLSearchParamsState.prototype = {
      type: U,
      bindURL: function (t) {
        (this.url = t), this.update();
      },
      parseObject: function (t) {
        var r,
          o,
          i,
          a,
          u,
          l,
          d,
          p = this.entries,
          v = N(t);
        if (v)
          for (o = (r = R(t, v)).next; !(i = c(o, r)).done; ) {
            if (
              ((u = (a = R(x(i.value))).next),
              (l = c(u, a)).done || (d = c(u, a)).done || !c(u, a).done)
            )
              throw new X("Expected sequence with length 2");
            ee(p, {key: P(l.value), value: P(d.value)});
          }
        else for (var h in t) w(t, h) && ee(p, {key: h, value: P(t[h])});
      },
      parseQuery: function (t) {
        if (t)
          for (var r, o, i = this.entries, a = oe(t, "&"), u = 0; u < a.length; )
            (r = a[u++]).length &&
              ((o = oe(r, "=")),
              ee(i, {key: deserialize(ne(o)), value: deserialize(Z(o, "="))}));
      },
      serialize: function () {
        for (var t, r = this.entries, o = [], i = 0; i < r.length; )
          (t = r[i++]), ee(o, serialize(t.key) + "=" + serialize(t.value));
        return Z(o, "&");
      },
      update: function () {
        (this.entries.length = 0), this.parseQuery(this.url.query);
      },
      updateURL: function () {
        this.url && this.url.update();
      },
    };
    var le = function URLSearchParams() {
        E(this, de);
        var t = arguments.length > 0 ? arguments[0] : void 0,
          r = D(this, new URLSearchParamsState(t));
        d || (this.size = r.entries.length);
      },
      de = le.prototype;
    if (
      (y(
        de,
        {
          append: function append(t, r) {
            var o = V(this);
            C(arguments.length, 2),
              ee(o.entries, {key: P(t), value: P(r)}),
              d || this.length++,
              o.updateURL();
          },
          delete: function (t) {
            for (
              var r = V(this),
                o = C(arguments.length, 1),
                i = r.entries,
                a = P(t),
                u = o < 2 ? void 0 : arguments[1],
                c = void 0 === u ? u : P(u),
                l = 0;
              l < i.length;

            ) {
              var p = i[l];
              if (p.key !== a || (void 0 !== c && p.value !== c)) l++;
              else if ((re(i, l, 1), void 0 !== c)) break;
            }
            d || (this.size = i.length), r.updateURL();
          },
          get: function get(t) {
            var r = V(this).entries;
            C(arguments.length, 1);
            for (var o = P(t), i = 0; i < r.length; i++)
              if (r[i].key === o) return r[i].value;
            return null;
          },
          getAll: function getAll(t) {
            var r = V(this).entries;
            C(arguments.length, 1);
            for (var o = P(t), i = [], a = 0; a < r.length; a++)
              r[a].key === o && ee(i, r[a].value);
            return i;
          },
          has: function has(t) {
            for (
              var r = V(this).entries,
                o = C(arguments.length, 1),
                i = P(t),
                a = o < 2 ? void 0 : arguments[1],
                u = void 0 === a ? a : P(a),
                c = 0;
              c < r.length;

            ) {
              var l = r[c++];
              if (l.key === i && (void 0 === u || l.value === u)) return !0;
            }
            return !1;
          },
          set: function set(t, r) {
            var o = V(this);
            C(arguments.length, 1);
            for (
              var i, a = o.entries, u = !1, c = P(t), l = P(r), p = 0;
              p < a.length;
              p++
            )
              (i = a[p]).key === c && (u ? re(a, p--, 1) : ((u = !0), (i.value = l)));
            u || ee(a, {key: c, value: l}), d || (this.size = a.length), o.updateURL();
          },
          sort: function sort() {
            var t = V(this);
            M(t.entries, function (t, r) {
              return t.key > r.key ? 1 : -1;
            }),
              t.updateURL();
          },
          forEach: function forEach(t) {
            for (
              var r,
                o = V(this).entries,
                i = S(t, arguments.length > 1 ? arguments[1] : void 0),
                a = 0;
              a < o.length;

            )
              i((r = o[a++]).value, r.key, this);
          },
          keys: function keys() {
            return new fe(this, "keys");
          },
          values: function values() {
            return new fe(this, "values");
          },
          entries: function entries() {
            return new fe(this, "entries");
          },
        },
        {enumerable: !0}
      ),
      v(de, j, de.entries, {name: "entries"}),
      v(
        de,
        "toString",
        function toString() {
          return V(this).serialize();
        },
        {enumerable: !0}
      ),
      d &&
        h(de, "size", {
          get: function size() {
            return V(this).entries.length;
          },
          configurable: !0,
          enumerable: !0,
        }),
      _(le, U),
      i({global: !0, constructor: !0, forced: !p}, {URLSearchParams: le}),
      !p && m(q))
    ) {
      var pe = l(G.has),
        ve = l(G.set),
        wrapRequestOptions = function (t) {
          if (I(t)) {
            var r,
              o = t.body;
            if (O(o) === U)
              return (
                (r = t.headers ? new q(t.headers) : new q()),
                pe(r, "content-type") ||
                  ve(
                    r,
                    "content-type",
                    "application/x-www-form-urlencoded;charset=UTF-8"
                  ),
                T(t, {body: A(0, P(o)), headers: A(0, r)})
              );
          }
          return t;
        };
      if (
        (m(B) &&
          i(
            {global: !0, enumerable: !0, dontCallGetSet: !0, forced: !0},
            {
              fetch: function fetch(t) {
                return B(
                  t,
                  arguments.length > 1 ? wrapRequestOptions(arguments[1]) : {}
                );
              },
            }
          ),
        m(H))
      ) {
        var he = function Request(t) {
          return (
            E(this, z),
            new H(t, arguments.length > 1 ? wrapRequestOptions(arguments[1]) : {})
          );
        };
        (z.constructor = he),
          (he.prototype = z),
          i(
            {global: !0, constructor: !0, dontCallGetSet: !0, forced: !0},
            {Request: he}
          );
      }
    }
    t.exports = {URLSearchParams: le, getState: V};
  },
  function (t, r, o) {
    "use strict";
    var i = o(23),
      a = o(30),
      u = o(135),
      c = o(98),
      l = o(326),
      d = o(17),
      p = TypeError,
      v = d("toPrimitive");
    t.exports = function (t, r) {
      if (!a(t) || u(t)) return t;
      var o,
        d = c(t, v);
      if (d) {
        if ((void 0 === r && (r = "default"), (o = i(d, t, r)), !a(o) || u(o)))
          return o;
        throw new p("Can't convert object to primitive value");
      }
      return void 0 === r && (r = "number"), l(t, r);
    };
  },
  function (t, r, o) {
    "use strict";
    var i = o(61);
    t.exports = i("document", "documentElement");
  },
  function (t, r, o) {
    "use strict";
    var i = o(13),
      a = o(15),
      u = Object.getOwnPropertyDescriptor;
    t.exports = function (t) {
      if (!a) return i[t];
      var r = u(i, t);
      return r && r.value;
    };
  },
  ,
  ,
  function (t, r, o) {
    "use strict";
    var i = o(13);
    t.exports = i;
  },
  function (t, r, o) {
    "use strict";
    var i = o(15),
      a = o(7),
      u = o(23),
      c = o(6),
      l = o(138),
      d = o(161),
      p = o(168),
      v = o(49),
      h = o(123),
      y = Object.assign,
      _ = Object.defineProperty,
      g = a([].concat);
    t.exports =
      !y ||
      c(function () {
        if (
          i &&
          1 !==
            y(
              {b: 1},
              y(
                _({}, "a", {
                  enumerable: !0,
                  get: function () {
                    _(this, "b", {value: 3, enumerable: !1});
                  },
                }),
                {b: 2}
              )
            ).b
        )
          return !0;
        var t = {},
          r = {},
          o = Symbol("assign detection"),
          a = "abcdefghijklmnopqrst";
        return (
          (t[o] = 7),
          a.split("").forEach(function (t) {
            r[t] = t;
          }),
          7 !== y({}, t)[o] || l(y({}, r)).join("") !== a
        );
      })
        ? function assign(t, r) {
            for (var o = v(t), a = arguments.length, c = 1, y = d.f, _ = p.f; a > c; )
              for (
                var b,
                  E = h(arguments[c++]),
                  m = y ? g(l(E), y(E)) : l(E),
                  w = m.length,
                  S = 0;
                w > S;

              )
                (b = m[S++]), (i && !u(_, E, b)) || (o[b] = E[b]);
            return o;
          }
        : y;
  },
  function (t, r, o) {
    var i = o(11).default,
      a = o(351);
    (t.exports = function toPropertyKey(t) {
      var r = a(t, "string");
      return "symbol" == i(r) ? r : r + "";
    }),
      (t.exports.__esModule = !0),
      (t.exports.default = t.exports);
  },
  ,
  ,
  ,
  ,
  ,
  ,
  function (t, r, o) {
    "use strict";
    var i = o(5),
      a = o(13),
      u = o(7),
      c = o(144),
      l = o(40),
      d = o(171),
      p = o(142),
      v = o(115),
      h = o(19),
      y = o(67),
      _ = o(30),
      g = o(6),
      b = o(194),
      E = o(70),
      m = o(193);
    t.exports = function (t, r, o) {
      var w = -1 !== t.indexOf("Map"),
        S = -1 !== t.indexOf("Weak"),
        O = w ? "set" : "add",
        x = a[t],
        I = x && x.prototype,
        P = x,
        T = {},
        fixMethod = function (t) {
          var r = u(I[t]);
          l(
            I,
            t,
            "add" === t
              ? function add(t) {
                  return r(this, 0 === t ? 0 : t), this;
                }
              : "delete" === t
              ? function (t) {
                  return !(S && !_(t)) && r(this, 0 === t ? 0 : t);
                }
              : "get" === t
              ? function get(t) {
                  return S && !_(t) ? void 0 : r(this, 0 === t ? 0 : t);
                }
              : "has" === t
              ? function has(t) {
                  return !(S && !_(t)) && r(this, 0 === t ? 0 : t);
                }
              : function set(t, o) {
                  return r(this, 0 === t ? 0 : t, o), this;
                }
          );
        };
      if (
        c(
          t,
          !h(x) ||
            !(
              S ||
              (I.forEach &&
                !g(function () {
                  new x().entries().next();
                }))
            )
        )
      )
        (P = o.getConstructor(r, t, w, O)), d.enable();
      else if (c(t, !0)) {
        var A = new P(),
          R = A[O](S ? {} : -0, 1) !== A,
          N = g(function () {
            A.has(1);
          }),
          L = b(function (t) {
            new x(t);
          }),
          C =
            !S &&
            g(function () {
              for (var t = new x(), r = 5; r--; ) t[O](r, r);
              return !t.has(-0);
            });
        L ||
          (((P = r(function (t, r) {
            v(t, I);
            var o = m(new x(), t, P);
            return y(r) || p(r, o[O], {that: o, AS_ENTRIES: w}), o;
          })).prototype = I),
          (I.constructor = P)),
          (N || C) && (fixMethod("delete"), fixMethod("has"), w && fixMethod("get")),
          (C || R) && fixMethod(O),
          S && I.clear && delete I.clear;
      }
      return (
        (T[t] = P),
        i({global: !0, constructor: !0, forced: P !== x}, T),
        E(P, t),
        S || o.setStrong(P, t, w),
        P
      );
    };
  },
  function (t, r, o) {
    var i = o(284);
    (t.exports = function _unsupportedIterableToArray(t, r) {
      if (t) {
        if ("string" == typeof t) return i(t, r);
        var o = Object.prototype.toString.call(t).slice(8, -1);
        return (
          "Object" === o && t.constructor && (o = t.constructor.name),
          "Map" === o || "Set" === o
            ? Array.from(t)
            : "Arguments" === o || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(o)
            ? i(t, r)
            : void 0
        );
      }
    }),
      (t.exports.__esModule = !0),
      (t.exports.default = t.exports);
  },
  function (t, r) {
    (t.exports = function _arrayLikeToArray(t, r) {
      (null == r || r > t.length) && (r = t.length);
      for (var o = 0, i = new Array(r); o < r; o++) i[o] = t[o];
      return i;
    }),
      (t.exports.__esModule = !0),
      (t.exports.default = t.exports);
  },
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  function (t, r, o) {
    "use strict";
    var i = TypeError;
    t.exports = function (t) {
      if (t > 9007199254740991) throw i("Maximum allowed index exceeded");
      return t;
    };
  },
  ,
  function (t, r, o) {
    "use strict";
    var i = o(6);
    t.exports = !i(function () {
      function F() {}
      return (
        (F.prototype.constructor = null), Object.getPrototypeOf(new F()) !== F.prototype
      );
    });
  },
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  function (t, r) {
    var o = (t.exports = {version: "2.6.12"});
    "number" == typeof __e && (__e = o);
  },
  function (t, r, o) {
    "use strict";
    var i = o(64),
      a = o(49),
      u = o(123),
      c = o(63),
      l = TypeError,
      d = "Reduce of empty array with no initial value",
      createMethod = function (t) {
        return function (r, o, p, v) {
          var h = a(r),
            y = u(h),
            _ = c(h);
          if ((i(o), 0 === _ && p < 2)) throw new l(d);
          var g = t ? _ - 1 : 0,
            b = t ? -1 : 1;
          if (p < 2)
            for (;;) {
              if (g in y) {
                (v = y[g]), (g += b);
                break;
              }
              if (((g += b), t ? g < 0 : _ <= g)) throw new l(d);
            }
          for (; t ? g >= 0 : _ > g; g += b) g in y && (v = o(v, y[g], g, h));
          return v;
        };
      };
    t.exports = {left: createMethod(!1), right: createMethod(!0)};
  },
  ,
  function (t, r, o) {
    "use strict";
    var i = o(23),
      a = o(19),
      u = o(30),
      c = TypeError;
    t.exports = function (t, r) {
      var o, l;
      if ("string" === r && a((o = t.toString)) && !u((l = i(o, t)))) return l;
      if (a((o = t.valueOf)) && !u((l = i(o, t)))) return l;
      if ("string" !== r && a((o = t.toString)) && !u((l = i(o, t)))) return l;
      throw new c("Can't convert object to primitive value");
    };
  },
  function (t, r, o) {
    "use strict";
    var i = o(23),
      a = o(61),
      u = o(17),
      c = o(40);
    t.exports = function () {
      var t = a("Symbol"),
        r = t && t.prototype,
        o = r && r.valueOf,
        l = u("toPrimitive");
      r &&
        !r[l] &&
        c(
          r,
          l,
          function (t) {
            return i(o, this);
          },
          {arity: 1}
        );
    };
  },
  ,
  function (t, r, o) {
    "use strict";
    var i = o(7),
      a = o(64);
    t.exports = function (t, r, o) {
      try {
        return i(a(Object.getOwnPropertyDescriptor(t, r)[o]));
      } catch (t) {}
    };
  },
  function (t, r, o) {
    "use strict";
    var i = o(6),
      a = o(30),
      u = o(51),
      c = o(331),
      l = Object.isExtensible,
      d = i(function () {
        l(1);
      });
    t.exports =
      d || c
        ? function isExtensible(t) {
            return !!a(t) && (!c || "ArrayBuffer" !== u(t)) && (!l || l(t));
          }
        : l;
  },
  function (t, r, o) {
    "use strict";
    var i = o(6);
    t.exports = i(function () {
      if ("function" == typeof ArrayBuffer) {
        var t = new ArrayBuffer(8);
        Object.isExtensible(t) && Object.defineProperty(t, "a", {value: 8});
      }
    });
  },
  ,
  function (t, r, o) {
    "use strict";
    var i = Math.ceil,
      a = Math.floor;
    t.exports =
      Math.trunc ||
      function trunc(t) {
        var r = +t;
        return (r > 0 ? a : i)(r);
      };
  },
  function (t, r, o) {
    "use strict";
    var i = o(88).forEach,
      a = o(134)("forEach");
    t.exports = a
      ? [].forEach
      : function forEach(t) {
          return i(this, t, arguments.length > 1 ? arguments[1] : void 0);
        };
  },
  function (t, r, o) {
    "use strict";
    var i = o(336),
      a = String,
      u = TypeError;
    t.exports = function (t) {
      if (i(t)) return t;
      throw new u("Can't set " + a(t) + " as a prototype");
    };
  },
  function (t, r, o) {
    "use strict";
    var i = o(30);
    t.exports = function (t) {
      return i(t) || null === t;
    };
  },
  function (t, r, o) {
    "use strict";
    var i = o(7),
      a = o(49),
      u = Math.floor,
      c = i("".charAt),
      l = i("".replace),
      d = i("".slice),
      p = /\$([$&'`]|\d{1,2}|<[^>]*>)/g,
      v = /\$([$&'`]|\d{1,2})/g;
    t.exports = function (t, r, o, i, h, y) {
      var _ = o + t.length,
        g = i.length,
        b = v;
      return (
        void 0 !== h && ((h = a(h)), (b = p)),
        l(y, b, function (a, l) {
          var p;
          switch (c(l, 0)) {
            case "$":
              return "$";
            case "&":
              return t;
            case "`":
              return d(r, 0, o);
            case "'":
              return d(r, _);
            case "<":
              p = h[d(l, 1, -1)];
              break;
            default:
              var v = +l;
              if (0 === v) return a;
              if (v > g) {
                var y = u(v / 10);
                return 0 === y
                  ? a
                  : y <= g
                  ? void 0 === i[y - 1]
                    ? c(l, 1)
                    : i[y - 1] + c(l, 1)
                  : a;
              }
              p = i[v - 1];
          }
          return void 0 === p ? "" : p;
        })
      );
    };
  },
  function (t, r) {
    (t.exports = function _arrayWithHoles(t) {
      if (Array.isArray(t)) return t;
    }),
      (t.exports.__esModule = !0),
      (t.exports.default = t.exports);
  },
  function (t, r) {
    (t.exports = function _nonIterableRest() {
      throw new TypeError(
        "Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."
      );
    }),
      (t.exports.__esModule = !0),
      (t.exports.default = t.exports);
  },
  function (t, r, o) {
    "use strict";
    var i = o(43).f;
    t.exports = function (t, r, o) {
      o in t ||
        i(t, o, {
          configurable: !0,
          get: function () {
            return r[o];
          },
          set: function (t) {
            r[o] = t;
          },
        });
    };
  },
  function (t, r, o) {
    "use strict";
    var i = o(7),
      a = o(172),
      u = o(171).getWeakData,
      c = o(115),
      l = o(34),
      d = o(67),
      p = o(30),
      v = o(142),
      h = o(88),
      y = o(31),
      _ = o(46),
      g = _.set,
      b = _.getterFor,
      E = h.find,
      m = h.findIndex,
      w = i([].splice),
      S = 0,
      uncaughtFrozenStore = function (t) {
        return t.frozen || (t.frozen = new UncaughtFrozenStore());
      },
      UncaughtFrozenStore = function () {
        this.entries = [];
      },
      findUncaughtFrozen = function (t, r) {
        return E(t.entries, function (t) {
          return t[0] === r;
        });
      };
    (UncaughtFrozenStore.prototype = {
      get: function (t) {
        var r = findUncaughtFrozen(this, t);
        if (r) return r[1];
      },
      has: function (t) {
        return !!findUncaughtFrozen(this, t);
      },
      set: function (t, r) {
        var o = findUncaughtFrozen(this, t);
        o ? (o[1] = r) : this.entries.push([t, r]);
      },
      delete: function (t) {
        var r = m(this.entries, function (r) {
          return r[0] === t;
        });
        return ~r && w(this.entries, r, 1), !!~r;
      },
    }),
      (t.exports = {
        getConstructor: function (t, r, o, i) {
          var h = t(function (t, a) {
              c(t, _),
                g(t, {type: r, id: S++, frozen: void 0}),
                d(a) || v(a, t[i], {that: t, AS_ENTRIES: o});
            }),
            _ = h.prototype,
            E = b(r),
            define = function (t, r, o) {
              var i = E(t),
                a = u(l(r), !0);
              return !0 === a ? uncaughtFrozenStore(i).set(r, o) : (a[i.id] = o), t;
            };
          return (
            a(_, {
              delete: function (t) {
                var r = E(this);
                if (!p(t)) return !1;
                var o = u(t);
                return !0 === o
                  ? uncaughtFrozenStore(r).delete(t)
                  : o && y(o, r.id) && delete o[r.id];
              },
              has: function has(t) {
                var r = E(this);
                if (!p(t)) return !1;
                var o = u(t);
                return !0 === o ? uncaughtFrozenStore(r).has(t) : o && y(o, r.id);
              },
            }),
            a(
              _,
              o
                ? {
                    get: function get(t) {
                      var r = E(this);
                      if (p(t)) {
                        var o = u(t);
                        return !0 === o
                          ? uncaughtFrozenStore(r).get(t)
                          : o
                          ? o[r.id]
                          : void 0;
                      }
                    },
                    set: function set(t, r) {
                      return define(this, t, r);
                    },
                  }
                : {
                    add: function add(t) {
                      return define(this, t, !0);
                    },
                  }
            ),
            h
          );
        },
      });
  },
  function (t, r, o) {
    "use strict";
    var i = o(5),
      a = o(13),
      u = o(23),
      c = o(7),
      l = o(60),
      d = o(15),
      p = o(104),
      v = o(6),
      h = o(31),
      y = o(78),
      _ = o(34),
      g = o(50),
      b = o(182),
      E = o(32),
      m = o(97),
      w = o(82),
      S = o(138),
      O = o(111),
      x = o(224),
      I = o(161),
      P = o(94),
      T = o(43),
      A = o(200),
      R = o(168),
      N = o(40),
      L = o(73),
      C = o(105),
      k = o(160),
      M = o(124),
      j = o(149),
      U = o(17),
      W = o(252),
      D = o(217),
      V = o(327),
      K = o(70),
      B = o(46),
      H = o(88).forEach,
      q = k("hidden"),
      z = "Symbol",
      G = B.set,
      Q = B.getterFor(z),
      X = Object.prototype,
      Y = a.Symbol,
      J = Y && Y.prototype,
      $ = a.RangeError,
      Z = a.TypeError,
      ee = a.QObject,
      te = P.f,
      ne = T.f,
      re = x.f,
      oe = R.f,
      ie = c([].push),
      ae = C("symbols"),
      ue = C("op-symbols"),
      ce = C("wks"),
      se = !ee || !ee.prototype || !ee.prototype.findChild,
      fallbackDefineProperty = function (t, r, o) {
        var i = te(X, r);
        i && delete X[r], ne(t, r, o), i && t !== X && ne(X, r, i);
      },
      fe =
        d &&
        v(function () {
          return (
            7 !==
            w(
              ne({}, "a", {
                get: function () {
                  return ne(this, "a", {value: 7}).a;
                },
              })
            ).a
          );
        })
          ? fallbackDefineProperty
          : ne,
      wrap = function (t, r) {
        var o = (ae[t] = w(J));
        return G(o, {type: z, tag: t, description: r}), d || (o.description = r), o;
      },
      le = function defineProperty(t, r, o) {
        t === X && le(ue, r, o), _(t);
        var i = b(r);
        return (
          _(o),
          h(ae, i)
            ? (o.enumerable
                ? (h(t, q) && t[q][i] && (t[q][i] = !1),
                  (o = w(o, {enumerable: m(0, !1)})))
                : (h(t, q) || ne(t, q, m(1, w(null))), (t[q][i] = !0)),
              fe(t, i, o))
            : ne(t, i, o)
        );
      },
      de = function defineProperties(t, r) {
        _(t);
        var o = g(r),
          i = S(o).concat($getOwnPropertySymbols(o));
        return (
          H(i, function (r) {
            (d && !u(pe, o, r)) || le(t, r, o[r]);
          }),
          t
        );
      },
      pe = function propertyIsEnumerable(t) {
        var r = b(t),
          o = u(oe, this, r);
        return (
          !(this === X && h(ae, r) && !h(ue, r)) &&
          (!(o || !h(this, r) || !h(ae, r) || (h(this, q) && this[q][r])) || o)
        );
      },
      ve = function getOwnPropertyDescriptor(t, r) {
        var o = g(t),
          i = b(r);
        if (o !== X || !h(ae, i) || h(ue, i)) {
          var a = te(o, i);
          return !a || !h(ae, i) || (h(o, q) && o[q][i]) || (a.enumerable = !0), a;
        }
      },
      he = function getOwnPropertyNames(t) {
        var r = re(g(t)),
          o = [];
        return (
          H(r, function (t) {
            h(ae, t) || h(M, t) || ie(o, t);
          }),
          o
        );
      },
      $getOwnPropertySymbols = function (t) {
        var r = t === X,
          o = re(r ? ue : g(t)),
          i = [];
        return (
          H(o, function (t) {
            !h(ae, t) || (r && !h(X, t)) || ie(i, ae[t]);
          }),
          i
        );
      };
    p ||
      ((Y = function Symbol() {
        if (y(J, this)) throw new Z("Symbol is not a constructor");
        var t = arguments.length && void 0 !== arguments[0] ? E(arguments[0]) : void 0,
          r = j(t),
          setter = function (t) {
            var o = void 0 === this ? a : this;
            o === X && u(setter, ue, t), h(o, q) && h(o[q], r) && (o[q][r] = !1);
            var i = m(1, t);
            try {
              fe(o, r, i);
            } catch (t) {
              if (!(t instanceof $)) throw t;
              fallbackDefineProperty(o, r, i);
            }
          };
        return d && se && fe(X, r, {configurable: !0, set: setter}), wrap(r, t);
      }),
      N((J = Y.prototype), "toString", function toString() {
        return Q(this).tag;
      }),
      N(Y, "withoutSetter", function (t) {
        return wrap(j(t), t);
      }),
      (R.f = pe),
      (T.f = le),
      (A.f = de),
      (P.f = ve),
      (O.f = x.f = he),
      (I.f = $getOwnPropertySymbols),
      (W.f = function (t) {
        return wrap(U(t), t);
      }),
      d &&
        (L(J, "description", {
          configurable: !0,
          get: function description() {
            return Q(this).description;
          },
        }),
        l || N(X, "propertyIsEnumerable", pe, {unsafe: !0}))),
      i({global: !0, constructor: !0, wrap: !0, forced: !p, sham: !p}, {Symbol: Y}),
      H(S(ce), function (t) {
        D(t);
      }),
      i(
        {target: z, stat: !0, forced: !p},
        {
          useSetter: function () {
            se = !0;
          },
          useSimple: function () {
            se = !1;
          },
        }
      ),
      i(
        {target: "Object", stat: !0, forced: !p, sham: !d},
        {
          create: function create(t, r) {
            return void 0 === r ? w(t) : de(w(t), r);
          },
          defineProperty: le,
          defineProperties: de,
          getOwnPropertyDescriptor: ve,
        }
      ),
      i({target: "Object", stat: !0, forced: !p}, {getOwnPropertyNames: he}),
      V(),
      K(Y, z),
      (M[q] = !0);
  },
  function (t, r, o) {
    "use strict";
    var i = o(143),
      a = o(166),
      u = o(30),
      c = o(17)("species"),
      l = Array;
    t.exports = function (t) {
      var r;
      return (
        i(t) &&
          ((r = t.constructor),
          ((a(r) && (r === l || i(r.prototype))) || (u(r) && null === (r = r[c]))) &&
            (r = void 0)),
        void 0 === r ? l : r
      );
    };
  },
  function (t, r, o) {
    "use strict";
    var i = o(5),
      a = o(61),
      u = o(31),
      c = o(32),
      l = o(105),
      d = o(253),
      p = l("string-to-symbol-registry"),
      v = l("symbol-to-string-registry");
    i(
      {target: "Symbol", stat: !0, forced: !d},
      {
        for: function (t) {
          var r = c(t);
          if (u(p, r)) return p[r];
          var o = a("Symbol")(r);
          return (p[r] = o), (v[o] = r), o;
        },
      }
    );
  },
  function (t, r, o) {
    "use strict";
    var i = o(5),
      a = o(31),
      u = o(135),
      c = o(110),
      l = o(105),
      d = o(253),
      p = l("symbol-to-string-registry");
    i(
      {target: "Symbol", stat: !0, forced: !d},
      {
        keyFor: function keyFor(t) {
          if (!u(t)) throw new TypeError(c(t) + " is not a symbol");
          if (a(p, t)) return p[t];
        },
      }
    );
  },
  function (t, r, o) {
    "use strict";
    var i = o(7),
      a = o(143),
      u = o(19),
      c = o(51),
      l = o(32),
      d = i([].push);
    t.exports = function (t) {
      if (u(t)) return t;
      if (a(t)) {
        for (var r = t.length, o = [], i = 0; i < r; i++) {
          var p = t[i];
          "string" == typeof p
            ? d(o, p)
            : ("number" != typeof p && "Number" !== c(p) && "String" !== c(p)) ||
              d(o, l(p));
        }
        var v = o.length,
          h = !0;
        return function (t, r) {
          if (h) return (h = !1), r;
          if (a(this)) return r;
          for (var i = 0; i < v; i++) if (o[i] === t) return r;
        };
      }
    };
  },
  function (t, r, o) {
    "use strict";
    var i = o(5),
      a = o(104),
      u = o(6),
      c = o(161),
      l = o(49);
    i(
      {
        target: "Object",
        stat: !0,
        forced:
          !a ||
          u(function () {
            c.f(1);
          }),
      },
      {
        getOwnPropertySymbols: function getOwnPropertySymbols(t) {
          var r = c.f;
          return r ? r(l(t)) : [];
        },
      }
    );
  },
  function (t, r, o) {
    "use strict";
    var i = o(34),
      a = o(256);
    t.exports = function (t, r, o, u) {
      try {
        return u ? r(i(o)[0], o[1]) : r(o);
      } catch (r) {
        a(t, "throw", r);
      }
    };
  },
  function (t, r, o) {
    "use strict";
    var i = o(199),
      a = o(109);
    t.exports = i
      ? {}.toString
      : function toString() {
          return "[object " + a(this) + "]";
        };
  },
  function (t, r) {
    (t.exports = function _iterableToArrayLimit(t, r) {
      var o =
        null == t
          ? null
          : ("undefined" != typeof Symbol && t[Symbol.iterator]) || t["@@iterator"];
      if (null != o) {
        var i,
          a,
          u,
          c,
          l = [],
          d = !0,
          p = !1;
        try {
          if (((u = (o = o.call(t)).next), 0 === r)) {
            if (Object(o) !== o) return;
            d = !1;
          } else
            for (
              ;
              !(d = (i = u.call(o)).done) && (l.push(i.value), l.length !== r);
              d = !0
            );
        } catch (t) {
          (p = !0), (a = t);
        } finally {
          try {
            if (!d && null != o.return && ((c = o.return()), Object(c) !== c)) return;
          } finally {
            if (p) throw a;
          }
        }
        return l;
      }
    }),
      (t.exports.__esModule = !0),
      (t.exports.default = t.exports);
  },
  function (t, r, o) {
    var i = o(11).default;
    (t.exports = function toPrimitive(t, r) {
      if ("object" != i(t) || !t) return t;
      var o = t[Symbol.toPrimitive];
      if (void 0 !== o) {
        var a = o.call(t, r || "default");
        if ("object" != i(a)) return a;
        throw new TypeError("@@toPrimitive must return a primitive value.");
      }
      return ("string" === r ? String : Number)(t);
    }),
      (t.exports.__esModule = !0),
      (t.exports.default = t.exports);
  },
  function (t, r, o) {
    "use strict";
    var i,
      a = o(221),
      u = o(13),
      c = o(7),
      l = o(172),
      d = o(171),
      p = o(282),
      v = o(341),
      h = o(30),
      y = o(46).enforce,
      _ = o(6),
      g = o(249),
      b = Object,
      E = Array.isArray,
      m = b.isExtensible,
      w = b.isFrozen,
      S = b.isSealed,
      O = b.freeze,
      x = b.seal,
      I = !u.ActiveXObject && "ActiveXObject" in u,
      wrapper = function (t) {
        return function WeakMap() {
          return t(this, arguments.length ? arguments[0] : void 0);
        };
      },
      P = p("WeakMap", wrapper, v),
      T = P.prototype,
      A = c(T.set);
    if (g)
      if (I) {
        (i = v.getConstructor(wrapper, "WeakMap", !0)), d.enable();
        var R = c(T.delete),
          N = c(T.has),
          L = c(T.get);
        l(T, {
          delete: function (t) {
            if (h(t) && !m(t)) {
              var r = y(this);
              return r.frozen || (r.frozen = new i()), R(this, t) || r.frozen.delete(t);
            }
            return R(this, t);
          },
          has: function has(t) {
            if (h(t) && !m(t)) {
              var r = y(this);
              return r.frozen || (r.frozen = new i()), N(this, t) || r.frozen.has(t);
            }
            return N(this, t);
          },
          get: function get(t) {
            if (h(t) && !m(t)) {
              var r = y(this);
              return (
                r.frozen || (r.frozen = new i()),
                N(this, t) ? L(this, t) : r.frozen.get(t)
              );
            }
            return L(this, t);
          },
          set: function set(t, r) {
            if (h(t) && !m(t)) {
              var o = y(this);
              o.frozen || (o.frozen = new i()),
                N(this, t) ? A(this, t, r) : o.frozen.set(t, r);
            } else A(this, t, r);
            return this;
          },
        });
      } else
        a &&
          _(function () {
            var t = O([]);
            return A(new P(), t, 1), !w(t);
          }) &&
          l(T, {
            set: function set(t, r) {
              var o;
              return (
                E(t) && (w(t) ? (o = O) : S(t) && (o = x)),
                A(this, t, r),
                o && o(t),
                this
              );
            },
          });
  },
  ,
  ,
  function (t, r, o) {
    "use strict";
    var i = o(15),
      a = o(6),
      u = o(7),
      c = o(170),
      l = o(138),
      d = o(50),
      p = u(o(168).f),
      v = u([].push),
      h =
        i &&
        a(function () {
          var t = Object.create(null);
          return (t[2] = 2), !p(t, 2);
        }),
      createMethod = function (t) {
        return function (r) {
          for (
            var o,
              a = d(r),
              u = l(a),
              y = h && null === c(a),
              _ = u.length,
              g = 0,
              b = [];
            _ > g;

          )
            (o = u[g++]), (i && !(y ? o in a : p(a, o))) || v(b, t ? [o, a[o]] : a[o]);
          return b;
        };
      };
    t.exports = {entries: createMethod(!0), values: createMethod(!1)};
  },
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  function (t, r, o) {
    "use strict";
    var i = o(110),
      a = TypeError;
    t.exports = function (t, r) {
      if (!delete t[r]) throw new a("Cannot delete property " + i(r) + " of " + i(t));
    };
  },
  ,
  function (t, r, o) {
    "use strict";
    var i = o(96).match(/AppleWebKit\/(\d+)\./);
    t.exports = !!i && +i[1];
  },
  ,
  ,
  function (t, r, o) {
    "use strict";
    var i = o(96).match(/firefox\/(\d+)/i);
    t.exports = !!i && +i[1];
  },
  function (t, r, o) {
    "use strict";
    var i = o(96);
    t.exports = /MSIE|Trident/.test(i);
  },
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  function (t, r, o) {
    "use strict";
    o(1),
      Object.defineProperty(r, "__esModule", {value: !0}),
      (r.Web3MessageToTopWindow = r.Web3MessageToIFrame = r.PostMessageAction = void 0);
    var i = (function (t) {
      return (
        (t.Acknowledged = "acknowledged"),
        (t.Connected = "connected"),
        (t.Event = "event"),
        (t.Exit = "exit"),
        (t.InternalEvent = "internal-event"),
        (t.Ready = "ready"),
        (t.ReadyForConfigure = "ready-for-configure"),
        (t.Resize = "resize"),
        (t.Result = "result"),
        (t.TrackingReady = "tracking-ready"),
        (t.Web3Message = "web3-message"),
        t
      );
    })({});
    r.PostMessageAction = i;
    var a = (function (t) {
      return (
        (t.PROVIDER_CONNECTED = "PROVIDER_CONNECTED"),
        (t.PROVIDER_ERROR = "PROVIDER_ERROR"),
        (t.PROVIDER_CHAIN_INCORRECT = "PROVIDER_CHAIN_INCORRECT"),
        (t.PROVIDER_CHAIN_ADD_REQUIRED = "PROVIDER_CHAIN_ADD_REQUIRED"),
        (t.PROVIDER_MANUAL_CHAIN_REQUIRED = "PROVIDER_MANUAL_CHAIN_REQUIRED"),
        (t.RESPONSE_WALLETCONNECT_V1_URI = "RESPONSE_WALLETCONNECT_V1_URI"),
        (t.RESPONSE_WALLETCONNECT_V2_URI = "RESPONSE_WALLETCONNECT_V2_URI"),
        (t.RESPONSE_COINBASE_WALLET_DATA = "RESPONSE_COINBASE_WALLET_DATA"),
        (t.RESPONSE_PLUGIN_DATA = "RESPONSE_PLUGIN_DATA"),
        (t.RESPONSE_WALLET_SIGNATURE = "RESPONSE_WALLET_SIGNATURE"),
        (t.RESPONSE_TORUS_ERROR = "RESPONSE_TORUS_ERROR"),
        (t.RESPONSE_TREZOR_ERROR = "RESPONSE_TREZOR_ERROR"),
        t
      );
    })({});
    r.Web3MessageToIFrame = a;
    var u = (function (t) {
      return (
        (t.OPEN_BROWSER_PLUGIN = "OPEN_BROWSER_PLUGIN"),
        (t.OPEN_URI = "OPEN_URI"),
        (t.REQUEST_WALLETCONNECT_V1_URI = "REQUEST_WALLETCONNECT_V1_URI"),
        (t.REQUEST_WALLETCONNECT_V2_URI = "REQUEST_WALLETCONNECT_V2_URI"),
        (t.REQUEST_COINBASE_WALLET_DATA = "REQUEST_COINBASE_WALLET_DATA"),
        (t.REQUEST_PLUGIN_DATA = "REQUEST_PLUGIN_DATA"),
        (t.REQUEST_CHAIN_SWITCH = "REQUEST_CHAIN_SWITCH"),
        (t.REQUEST_CHAIN_ADD = "REQUEST_CHAIN_ADD"),
        (t.REQUEST_WALLET_SIGNATURE = "REQUEST_WALLET_SIGNATURE"),
        (t.REQUEST_TREZOR_DATA = "REQUEST_TREZOR_DATA"),
        (t.COPY_TO_CLIPBOARD = "COPY_TO_CLIPBOARD"),
        (t.OPEN_MEW_PLUGIN = "OPEN_MEW_PLUGIN"),
        (t.OPEN_TORUS_CONNECT = "OPEN_TORUS_CONNECT"),
        (t.START_BRIDGE = "START_BRIDGE"),
        t
      );
    })({});
    r.Web3MessageToTopWindow = u;
  },
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  function (t, r, o) {
    "use strict";
    o(1);
    var i = o(2);
    Object.defineProperty(r, "__esModule", {value: !0}),
      (r.default = void 0),
      o(25),
      o(58),
      o(118);
    var a = i(o(400));
    r.default = function _default() {
      if (null == window.navigator)
        return {
          browserLanguage: "",
          isAndroid: !1,
          isIE: !1,
          isIOS: !1,
          isIOSChrome: !1,
          isMobile: !1,
          isMac: !1,
          isWindows: !1,
          isLinux: !1,
        };
      var t = window.navigator,
        r = (function () {
          if (null != t.language && "" !== t.language) return t.language;
          var r = t.userLanguage;
          return null != r ? r : "";
        })(),
        o = /windows phone/i.test(t.userAgent),
        i = /android|silk/i.test(t.userAgent) && !o,
        u = /MSIE |Trident/i.test(t.userAgent),
        c = /iPad|iPhone|iPod/.test(t.userAgent) && !window.MSStream && !o,
        l = -1 !== t.platform.indexOf("Win"),
        d = -1 !== t.platform.indexOf("Mac"),
        p = -1 !== t.platform.indexOf("Linux"),
        v = c && !/Safari/i.test(t.userAgent);
      return {
        browserLanguage: r,
        isAndroid: i,
        isIE: u,
        isIOS: c,
        isIOSChrome: (0, a.default)().isIOSChrome,
        isMobile: (0, a.default)().isMobile,
        isWindows: l,
        isMac: d,
        isLinux: p,
        isIOSEmbeddedWebview: v,
      };
    };
  },
  ,
  ,
  ,
  ,
  function (t, r, o) {
    "use strict";
    o(1),
      Object.defineProperty(r, "__esModule", {value: !0}),
      (r.default = void 0),
      o(25),
      o(58);
    r.default = function _default() {
      if (null == window.navigator) return {isIOSChrome: !1, isMobile: !1};
      var t = window.navigator,
        r = /windows phone/i.test(t.userAgent),
        o = /android|silk/i.test(t.userAgent) && !r,
        i = /iPad|iPhone|iPod/.test(t.userAgent) && !window.MSStream && !r;
      return {
        isIOSChrome: /CriOS/.test(t.userAgent),
        isMobile: i || o || r || /Mobi/i.test(t.userAgent),
      };
    };
  },
  ,
  ,
  ,
  ,
  function (t, r, o) {
    var i = o(425),
      a = o(323),
      u = o(665),
      c = o(525),
      l = o(524),
      $export = function (t, r, o) {
        var d,
          p,
          v,
          h = t & $export.F,
          y = t & $export.G,
          _ = t & $export.S,
          g = t & $export.P,
          b = t & $export.B,
          E = t & $export.W,
          m = y ? a : a[r] || (a[r] = {}),
          w = m.prototype,
          S = y ? i : _ ? i[r] : (i[r] || {}).prototype;
        for (d in (y && (o = r), o))
          ((p = !h && S && void 0 !== S[d]) && l(m, d)) ||
            ((v = p ? S[d] : o[d]),
            (m[d] =
              y && "function" != typeof S[d]
                ? o[d]
                : b && p
                ? u(v, i)
                : E && S[d] == v
                ? (function (t) {
                    var F = function (r, o, i) {
                      if (this instanceof t) {
                        switch (arguments.length) {
                          case 0:
                            return new t();
                          case 1:
                            return new t(r);
                          case 2:
                            return new t(r, o);
                        }
                        return new t(r, o, i);
                      }
                      return t.apply(this, arguments);
                    };
                    return (F.prototype = t.prototype), F;
                  })(v)
                : g && "function" == typeof v
                ? u(Function.call, v)
                : v),
            g &&
              (((m.virtual || (m.virtual = {}))[d] = v),
              t & $export.R && w && !w[d] && c(w, d, v)));
      };
    ($export.F = 1),
      ($export.G = 2),
      ($export.S = 4),
      ($export.P = 8),
      ($export.B = 16),
      ($export.W = 32),
      ($export.U = 64),
      ($export.R = 128),
      (t.exports = $export);
  },
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  function (t, r, o) {
    "use strict";
    o(1), Object.defineProperty(r, "__esModule", {value: !0}), (r.default = void 0);
    var i = function getApiUrl(t) {
      switch (t) {
        case "sandbox":
          return "https://sandbox.plaid.com";
        case "development":
          return "https://development.plaid.com";
        case "production":
          return "https://production.plaid.com";
        default:
          throw new Error("Invalid environment: ".concat(t));
      }
    };
    r.default = i;
  },
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  function (t, r) {
    var o = (t.exports =
      "undefined" != typeof window && window.Math == Math
        ? window
        : "undefined" != typeof self && self.Math == Math
        ? self
        : Function("return this")());
    "number" == typeof __g && (__g = o);
  },
  function (t, r, o) {
    var i = o(1132)("wks"),
      a = o(1111),
      u = o(425).Symbol,
      c = "function" == typeof u;
    (t.exports = function (t) {
      return i[t] || (i[t] = (c && u[t]) || (c ? u : a)("Symbol." + t));
    }).store = i;
  },
  function (t, r, o) {
    t.exports = !o(595)(function () {
      return (
        7 !=
        Object.defineProperty({}, "a", {
          get: function () {
            return 7;
          },
        }).a
      );
    });
  },
  ,
  ,
  ,
  ,
  ,
  ,
  function (t, r, o) {
    var i = o(523),
      a = o(1385),
      u = o(1131),
      c = Object.defineProperty;
    r.f = o(427)
      ? Object.defineProperty
      : function defineProperty(t, r, o) {
          if ((i(t), (r = u(r, !0)), i(o), a))
            try {
              return c(t, r, o);
            } catch (t) {}
          if ("get" in o || "set" in o) throw TypeError("Accessors not supported!");
          return "value" in o && (t[r] = o.value), t;
        };
  },
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  function (t, r) {
    t.exports = function (t) {
      return "object" == typeof t ? null !== t : "function" == typeof t;
    };
  },
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  function (t, r) {
    (t.exports = function _interopRequireDefault(t) {
      return t && t.__esModule ? t : {default: t};
    }),
      (t.exports.__esModule = !0),
      (t.exports.default = t.exports);
  },
  ,
  function (t, r, o) {
    t.exports = o(1447);
  },
  ,
  function (t, r, o) {
    var i = o(1144),
      a = o(1129);
    t.exports = function (t) {
      return i(a(t));
    };
  },
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  function (t, r, o) {
    var i = o(483);
    t.exports = function (t) {
      if (!i(t)) throw TypeError(t + " is not an object!");
      return t;
    };
  },
  function (t, r) {
    var o = {}.hasOwnProperty;
    t.exports = function (t, r) {
      return o.call(t, r);
    };
  },
  function (t, r, o) {
    var i = o(434),
      a = o(721);
    t.exports = o(427)
      ? function (t, r, o) {
          return i.f(t, r, a(1, o));
        }
      : function (t, r, o) {
          return (t[r] = o), t;
        };
  },
  ,
  function (t, r, o) {
    var i = o(1130),
      a = o(1146);
    function _typeof(r) {
      return (
        (t.exports = _typeof =
          "function" == typeof i && "symbol" == typeof a
            ? function (t) {
                return typeof t;
              }
            : function (t) {
                return t &&
                  "function" == typeof i &&
                  t.constructor === i &&
                  t !== i.prototype
                  ? "symbol"
                  : typeof t;
              }),
        (t.exports.__esModule = !0),
        (t.exports.default = t.exports),
        _typeof(r)
      );
    }
    (t.exports = _typeof), (t.exports.__esModule = !0), (t.exports.default = t.exports);
  },
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  function (t, r, o) {
    var i = o(1417),
      a = o(1424);
    (t.exports = function _defineProperty(t, r, o) {
      return (
        (r = a(r)) in t
          ? i(t, r, {value: o, enumerable: !0, configurable: !0, writable: !0})
          : (t[r] = o),
        t
      );
    }),
      (t.exports.__esModule = !0),
      (t.exports.default = t.exports);
  },
  ,
  function (t, r, o) {
    t.exports = o(1445);
  },
  function (t, r, o) {
    t.exports = o(1449);
  },
  ,
  ,
  ,
  function (t, r) {
    t.exports = function (t) {
      try {
        return !!t();
      } catch (t) {
        return !0;
      }
    };
  },
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  function (t, r, o) {
    t.exports = o(1450);
  },
  function (t, r, o) {
    var i = o(1379);
    t.exports = function (t, r, o) {
      if ((i(t), void 0 === r)) return t;
      switch (o) {
        case 1:
          return function (o) {
            return t.call(r, o);
          };
        case 2:
          return function (o, i) {
            return t.call(r, o, i);
          };
        case 3:
          return function (o, i, a) {
            return t.call(r, o, i, a);
          };
      }
      return function () {
        return t.apply(r, arguments);
      };
    };
  },
  function (t, r, o) {
    var i = o(1129);
    t.exports = function (t) {
      return Object(i(t));
    };
  },
  function (t, r, o) {
    var i = o(1386),
      a = o(1136);
    t.exports =
      Object.keys ||
      function keys(t) {
        return i(t, a);
      };
  },
  function (t, r, o) {
    var i = o(483);
    t.exports = function (t, r) {
      if (!i(t) || t._t !== r)
        throw TypeError("Incompatible receiver, " + r + " required!");
      return t;
    };
  },
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  function (t, r) {
    t.exports = function (t, r) {
      return {
        enumerable: !(1 & t),
        configurable: !(2 & t),
        writable: !(4 & t),
        value: r,
      };
    };
  },
  function (t, r) {
    t.exports = {};
  },
  function (t, r, o) {
    var i = o(665),
      a = o(1388),
      u = o(1389),
      c = o(523),
      l = o(1113),
      d = o(1390),
      p = {},
      v = {};
    ((r = t.exports =
      function (t, r, o, h, y) {
        var _,
          g,
          b,
          E,
          m = y
            ? function () {
                return t;
              }
            : d(t),
          w = i(o, h, r ? 2 : 1),
          S = 0;
        if ("function" != typeof m) throw TypeError(t + " is not iterable!");
        if (u(m)) {
          for (_ = l(t.length); _ > S; S++)
            if ((E = r ? w(c((g = t[S]))[0], g[1]) : w(t[S])) === p || E === v)
              return E;
        } else
          for (b = m.call(t); !(g = b.next()).done; )
            if ((E = a(b, w, g.value, r)) === p || E === v) return E;
      }).BREAK = p),
      (r.RETURN = v);
  },
  ,
  ,
  ,
  ,
  function (t, r) {
    r.f = {}.propertyIsEnumerable;
  },
  ,
  ,
  ,
  ,
  ,
  function (t, r, o) {
    var i = o(1111)("meta"),
      a = o(483),
      u = o(524),
      c = o(434).f,
      l = 0,
      d =
        Object.isExtensible ||
        function () {
          return !0;
        },
      p = !o(595)(function () {
        return d(Object.preventExtensions({}));
      }),
      setMeta = function (t) {
        c(t, i, {value: {i: "O" + ++l, w: {}}});
      },
      v = (t.exports = {
        KEY: i,
        NEED: !1,
        fastKey: function (t, r) {
          if (!a(t))
            return "symbol" == typeof t ? t : ("string" == typeof t ? "S" : "P") + t;
          if (!u(t, i)) {
            if (!d(t)) return "F";
            if (!r) return "E";
            setMeta(t);
          }
          return t[i].i;
        },
        getWeak: function (t, r) {
          if (!u(t, i)) {
            if (!d(t)) return !0;
            if (!r) return !1;
            setMeta(t);
          }
          return t[i].w;
        },
        onFreeze: function (t) {
          return p && v.NEED && d(t) && !u(t, i) && setMeta(t), t;
        },
      });
  },
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  function (t, r) {
    t.exports = !0;
  },
  function (t, r, o) {
    var i = o(434).f,
      a = o(524),
      u = o(426)("toStringTag");
    t.exports = function (t, r, o) {
      t && !a((t = o ? t : t.prototype), u) && i(t, u, {configurable: !0, value: r});
    };
  },
  function (t, r, o) {
    "use strict";
    var i = o(1439)(!0);
    o(1138)(
      String,
      "String",
      function (t) {
        (this._t = String(t)), (this._i = 0);
      },
      function () {
        var t,
          r = this._t,
          o = this._i;
        return o >= r.length
          ? {value: void 0, done: !0}
          : ((t = i(r, o)), (this._i += t.length), {value: t, done: !1});
      }
    );
  },
  ,
  function (t, r) {
    var o = 0,
      i = Math.random();
    t.exports = function (t) {
      return "Symbol(".concat(void 0 === t ? "" : t, ")_", (++o + i).toString(36));
    };
  },
  function (t, r, o) {
    r.f = o(426);
  },
  function (t, r, o) {
    var i = o(1134),
      a = Math.min;
    t.exports = function (t) {
      return t > 0 ? a(i(t), 9007199254740991) : 0;
    };
  },
  function (t, r) {},
  function (t, r, o) {
    o(1441);
    for (
      var i = o(425),
        a = o(525),
        u = o(722),
        c = o(426)("toStringTag"),
        l =
          "CSSRuleList,CSSStyleDeclaration,CSSValueList,ClientRectList,DOMRectList,DOMStringList,DOMTokenList,DataTransferItemList,FileList,HTMLAllCollection,HTMLCollection,HTMLFormElement,HTMLSelectElement,MediaList,MimeTypeArray,NamedNodeMap,NodeList,PaintRequestList,Plugin,PluginArray,SVGLengthList,SVGNumberList,SVGPathSegList,SVGPointList,SVGStringList,SVGTransformList,SourceBufferList,StyleSheetList,TextTrackCueList,TextTrackList,TouchList".split(
            ","
          ),
        d = 0;
      d < l.length;
      d++
    ) {
      var p = l[d],
        v = i[p],
        h = v && v.prototype;
      h && !h[c] && a(h, c, p), (u[p] = u.Array);
    }
  },
  function (t, r) {
    r.f = Object.getOwnPropertySymbols;
  },
  function (t, r, o) {
    t.exports = o(1459);
  },
  function (t, r, o) {
    t.exports = o(1491);
  },
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  function (t, r) {
    var o = {}.toString;
    t.exports = function (t) {
      return o.call(t).slice(8, -1);
    };
  },
  function (t, r, o) {
    var i = o(523),
      a = o(1434),
      u = o(1136),
      c = o(1135)("IE_PROTO"),
      Empty = function () {},
      createDict = function () {
        var t,
          r = o(1381)("iframe"),
          i = u.length;
        for (
          r.style.display = "none",
            o(1423).appendChild(r),
            r.src = "javascript:",
            (t = r.contentWindow.document).open(),
            t.write("<script>document.F=Object</script>"),
            t.close(),
            createDict = t.F;
          i--;

        )
          delete createDict.prototype[u[i]];
        return createDict();
      };
    t.exports =
      Object.create ||
      function create(t, r) {
        var o;
        return (
          null !== t
            ? ((Empty.prototype = i(t)),
              (o = new Empty()),
              (Empty.prototype = null),
              (o[c] = t))
            : (o = createDict()),
          void 0 === r ? o : a(o, r)
        );
      };
  },
  function (t, r, o) {
    var i = o(728),
      a = o(721),
      u = o(497),
      c = o(1131),
      l = o(524),
      d = o(1385),
      p = Object.getOwnPropertyDescriptor;
    r.f = o(427)
      ? p
      : function getOwnPropertyDescriptor(t, r) {
          if (((t = u(t)), (r = c(r, !0)), d))
            try {
              return p(t, r);
            } catch (t) {}
          if (l(t, r)) return a(!i.f.call(t, r), t[r]);
        };
  },
  function (t, r) {
    t.exports = function (t) {
      if (null == t) throw TypeError("Can't call method on  " + t);
      return t;
    };
  },
  function (t, r, o) {
    t.exports = o(1430);
  },
  function (t, r, o) {
    var i = o(483);
    t.exports = function (t, r) {
      if (!i(t)) return t;
      var o, a;
      if (r && "function" == typeof (o = t.toString) && !i((a = o.call(t)))) return a;
      if ("function" == typeof (o = t.valueOf) && !i((a = o.call(t)))) return a;
      if (!r && "function" == typeof (o = t.toString) && !i((a = o.call(t)))) return a;
      throw TypeError("Can't convert object to primitive value");
    };
  },
  function (t, r, o) {
    var i = o(323),
      a = o(425),
      u = "__core-js_shared__",
      c = a[u] || (a[u] = {});
    (t.exports = function (t, r) {
      return c[t] || (c[t] = void 0 !== r ? r : {});
    })("versions", []).push({
      version: i.version,
      mode: o(1107) ? "pure" : "global",
      copyright: "© 2020 Denis Pushkarev (zloirock.ru)",
    });
  },
  function (t, r, o) {
    var i = o(425),
      a = o(323),
      u = o(1107),
      c = o(1112),
      l = o(434).f;
    t.exports = function (t) {
      var r = a.Symbol || (a.Symbol = u ? {} : i.Symbol || {});
      "_" == t.charAt(0) || t in r || l(r, t, {value: c.f(t)});
    };
  },
  function (t, r) {
    var o = Math.ceil,
      i = Math.floor;
    t.exports = function (t) {
      return isNaN((t = +t)) ? 0 : (t > 0 ? i : o)(t);
    };
  },
  function (t, r, o) {
    var i = o(1132)("keys"),
      a = o(1111);
    t.exports = function (t) {
      return i[t] || (i[t] = a(t));
    };
  },
  function (t, r) {
    t.exports =
      "constructor,hasOwnProperty,isPrototypeOf,propertyIsEnumerable,toLocaleString,toString,valueOf".split(
        ","
      );
  },
  function (t, r, o) {
    var i = o(1386),
      a = o(1136).concat("length", "prototype");
    r.f =
      Object.getOwnPropertyNames ||
      function getOwnPropertyNames(t) {
        return i(t, a);
      };
  },
  function (t, r, o) {
    "use strict";
    var i = o(1107),
      a = o(405),
      u = o(1143),
      c = o(525),
      l = o(722),
      d = o(1440),
      p = o(1108),
      v = o(1420),
      h = o(426)("iterator"),
      y = !([].keys && "next" in [].keys()),
      _ = "keys",
      g = "values",
      returnThis = function () {
        return this;
      };
    t.exports = function (t, r, o, b, E, m, w) {
      d(o, r, b);
      var S,
        O,
        x,
        getMethod = function (t) {
          if (!y && t in A) return A[t];
          switch (t) {
            case _:
              return function keys() {
                return new o(this, t);
              };
            case g:
              return function values() {
                return new o(this, t);
              };
          }
          return function entries() {
            return new o(this, t);
          };
        },
        I = r + " Iterator",
        P = E == g,
        T = !1,
        A = t.prototype,
        R = A[h] || A["@@iterator"] || (E && A[E]),
        N = R || getMethod(E),
        L = E ? (P ? getMethod("entries") : N) : void 0,
        C = ("Array" == r && A.entries) || R;
      if (
        (C &&
          (x = v(C.call(new t()))) !== Object.prototype &&
          x.next &&
          (p(x, I, !0), i || "function" == typeof x[h] || c(x, h, returnThis)),
        P &&
          R &&
          R.name !== g &&
          ((T = !0),
          (N = function values() {
            return R.call(this);
          })),
        (i && !w) || (!y && !T && A[h]) || c(A, h, N),
        (l[r] = N),
        (l[I] = returnThis),
        E)
      )
        if (
          ((S = {values: P ? N : getMethod(g), keys: m ? N : getMethod(_), entries: L}),
          w)
        )
          for (O in S) O in A || u(A, O, S[O]);
        else a(a.P + a.F * (y || T), r, S);
      return S;
    };
  },
  function (t, r, o) {
    var i = o(525);
    t.exports = function (t, r, o) {
      for (var a in r) o && t[a] ? (t[a] = r[a]) : i(t, a, r[a]);
      return t;
    };
  },
  function (t, r) {
    t.exports = function (t, r, o, i) {
      if (!(t instanceof r) || (void 0 !== i && i in t))
        throw TypeError(o + ": incorrect invocation!");
      return t;
    };
  },
  ,
  ,
  function (t, r, o) {
    t.exports = o(525);
  },
  function (t, r, o) {
    var i = o(1126);
    t.exports = Object("z").propertyIsEnumerable(0)
      ? Object
      : function (t) {
          return "String" == i(t) ? t.split("") : Object(t);
        };
  },
  function (t, r, o) {
    var i = o(1126);
    t.exports =
      Array.isArray ||
      function isArray(t) {
        return "Array" == i(t);
      };
  },
  function (t, r, o) {
    t.exports = o(1438);
  },
  function (t, r, o) {
    "use strict";
    var i = o(425),
      a = o(405),
      u = o(734),
      c = o(595),
      l = o(525),
      d = o(1139),
      p = o(723),
      v = o(1140),
      h = o(483),
      y = o(1108),
      _ = o(434).f,
      g = o(1158)(0),
      b = o(427);
    t.exports = function (t, r, o, E, m, w) {
      var S = i[t],
        O = S,
        x = m ? "set" : "add",
        I = O && O.prototype,
        P = {};
      return (
        b &&
        "function" == typeof O &&
        (w ||
          (I.forEach &&
            !c(function () {
              new O().entries().next();
            })))
          ? ((O = r(function (r, o) {
              v(r, O, t, "_c"), (r._c = new S()), null != o && p(o, m, r[x], r);
            })),
            g(
              "add,clear,delete,forEach,get,has,set,keys,values,entries,toJSON".split(
                ","
              ),
              function (t) {
                var r = "add" == t || "set" == t;
                !(t in I) ||
                  (w && "clear" == t) ||
                  l(O.prototype, t, function (o, i) {
                    if ((v(this, O, t), !r && w && !h(o))) return "get" == t && void 0;
                    var a = this._c[t](0 === o ? 0 : o, i);
                    return r ? this : a;
                  });
              }
            ),
            w ||
              _(O.prototype, "size", {
                get: function () {
                  return this._c.size;
                },
              }))
          : ((O = E.getConstructor(r, t, m, x)), d(O.prototype, o), (u.NEED = !0)),
        y(O, t),
        (P[t] = O),
        a(a.G + a.W + a.F, P),
        w || E.setStrong(O, t, m),
        O
      );
    };
  },
  function (t, r, o) {
    "use strict";
    var i = o(405);
    t.exports = function (t) {
      i(i.S, t, {
        of: function of() {
          for (var t = arguments.length, r = new Array(t); t--; ) r[t] = arguments[t];
          return new this(r);
        },
      });
    };
  },
  function (t, r, o) {
    "use strict";
    var i = o(405),
      a = o(1379),
      u = o(665),
      c = o(723);
    t.exports = function (t) {
      i(i.S, t, {
        from: function from(t) {
          var r,
            o,
            i,
            l,
            d = arguments[1];
          return (
            a(this),
            (r = void 0 !== d) && a(d),
            null == t
              ? new this()
              : ((o = []),
                r
                  ? ((i = 0),
                    (l = u(d, arguments[2], 2)),
                    c(t, !1, function (t) {
                      o.push(l(t, i++));
                    }))
                  : c(t, !1, o.push, o),
                new this(o))
          );
        },
      });
    };
  },
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  function (t, r, o) {
    var i = o(665),
      a = o(1144),
      u = o(666),
      c = o(1113),
      l = o(1443);
    t.exports = function (t, r) {
      var o = 1 == t,
        d = 2 == t,
        p = 3 == t,
        v = 4 == t,
        h = 6 == t,
        y = 5 == t || h,
        _ = r || l;
      return function (r, l, g) {
        for (
          var b,
            E,
            m = u(r),
            w = a(m),
            S = i(l, g, 3),
            O = c(w.length),
            x = 0,
            I = o ? _(r, O) : d ? _(r, 0) : void 0;
          O > x;
          x++
        )
          if ((y || x in w) && ((E = S((b = w[x]), x, m)), t))
            if (o) I[x] = E;
            else if (E)
              switch (t) {
                case 3:
                  return !0;
                case 5:
                  return b;
                case 6:
                  return x;
                case 2:
                  I.push(b);
              }
            else if (v) return !1;
        return h ? -1 : p || v ? v : I;
      };
    };
  },
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  function (t, r, o) {
    "use strict";
    var i = o(495);
    o(1), o(3), o(18), Object.defineProperty(r, "__esModule", {value: !0});
    var a = {
      getMetaViewport: !0,
      isInlineStylesheetSupported: !0,
      isMetaViewportSet: !0,
    };
    (r.isMetaViewportSet = r.isInlineStylesheetSupported = r.getMetaViewport = void 0),
      o(25),
      o(58);
    var u = o(1397);
    i(u).forEach(function (t) {
      "default" !== t &&
        "__esModule" !== t &&
        (Object.prototype.hasOwnProperty.call(a, t) ||
          (t in r && r[t] === u[t]) ||
          Object.defineProperty(r, t, {
            enumerable: !0,
            get: function get() {
              return u[t];
            },
          }));
    });
    var c = function getMetaViewport() {
      var t = document.querySelectorAll('meta[name="viewport"]');
      if (0 === t.length) return "";
      var r = t[t.length - 1].getAttribute("content");
      return String(r);
    };
    r.getMetaViewport = c;
    r.isInlineStylesheetSupported = function isInlineStylesheetSupported() {
      try {
        var t = "link-stylesheet-test-".concat(Math.floor(100 * Math.random())),
          r = document.createElement("div");
        r.id = t;
        var o = document.createElement("style");
        o.textContent = "#".concat(t, " { width: 100px; height: 100px; }");
        var i = document.body;
        i.appendChild(r), i.appendChild(o);
        var a = 100 === r.offsetWidth;
        return i.removeChild(r), i.removeChild(o), a;
      } catch (t) {
        return !1;
      }
    };
    r.isMetaViewportSet = function isMetaViewportSet() {
      return /device-width/.test(c());
    };
  },
  function (t, r, o) {
    "use strict";
    o(1);
    var i = o(493);
    Object.defineProperty(r, "__esModule", {value: !0}),
      (r.FLEX_LINK_HTML_PATH = r.CREATE_PARAMETERS = void 0),
      Object.defineProperty(r, "LINK_CLIENT_CORS_ORIGIN", {
        enumerable: !0,
        get: function get() {
          return u.LINK_CLIENT_CORS_ORIGIN;
        },
      }),
      Object.defineProperty(r, "LINK_CLIENT_STABLE_URL", {
        enumerable: !0,
        get: function get() {
          return u.LINK_CLIENT_STABLE_URL;
        },
      }),
      Object.defineProperty(r, "LINK_CLIENT_URL", {
        enumerable: !0,
        get: function get() {
          return u.LINK_CLIENT_URL;
        },
      }),
      Object.defineProperty(r, "LINK_HTML_PATH", {
        enumerable: !0,
        get: function get() {
          return u.LINK_HTML_PATH;
        },
      }),
      Object.defineProperty(r, "PLAID_INTERNAL_NAMESPACE", {
        enumerable: !0,
        get: function get() {
          return u.PLAID_INTERNAL_NAMESPACE;
        },
      }),
      o(37);
    var a = i(o(1501)),
      u = o(231);
    r.FLEX_LINK_HTML_PATH = "/flink.html";
    var c = [].concat((0, a.default)(u.CREATE_PARAMETERS), [
      "apiVersion",
      "clientName",
      "configUserId",
      "configUserTags",
      "countryCodes",
      "customizations",
      "depositSwitchToken",
      "experimentVariants",
      "forceIframe",
      "hostedLinkVersion",
      "isEmbedded",
      "isSimpleIntegration",
      "key",
      "language",
      "linkCustomizationName",
      "longtail",
      "longTail",
      "oauthNonce",
      "oauthStateId",
      "oauthRedirectUri",
      "onResult",
      "paymentToken",
      "product",
      "accountSubtypes",
      "selectAccount",
      "noLoadingState",
      "useMobileWindow",
      "user",
      "userLegalName",
      "userEmailAddress",
      "userPhoneNumber",
      "webhook",
      "workflowVersionOverride",
    ]);
    r.CREATE_PARAMETERS = c;
  },
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  function (t, r, o) {
    "use strict";
    o(1),
      Object.defineProperty(r, "__esModule", {value: !0}),
      (r.ProviderRpcErrorCode = r.ChainTypes = void 0);
    var i = (function (t) {
      return (
        (t[(t.ACCOUNT_ACCESS_REJECTED = 4001)] = "ACCOUNT_ACCESS_REJECTED"),
        (t[(t.ACCOUNT_ACCESS_ALREADY_REQUESTED = -32002)] =
          "ACCOUNT_ACCESS_ALREADY_REQUESTED"),
        (t[(t.UNAUTHORIZED = 4100)] = "UNAUTHORIZED"),
        (t[(t.INVALID_PARAMS = -32602)] = "INVALID_PARAMS"),
        (t[(t.UNSUPPORTED_METHOD = 4200)] = "UNSUPPORTED_METHOD"),
        (t[(t.DISCONNECTED = 4900)] = "DISCONNECTED"),
        (t[(t.CHAIN_DISCONNECTED = 4901)] = "CHAIN_DISCONNECTED"),
        (t[(t.CHAIN_NOT_ADDED = 4902)] = "CHAIN_NOT_ADDED"),
        (t[(t.DOES_NOT_EXIST = -32601)] = "DOES_NOT_EXIST"),
        (t[(t.METAMASK_NETWORK_SWITCH_DISCONNECT = 1013)] =
          "METAMASK_NETWORK_SWITCH_DISCONNECT"),
        t
      );
    })({});
    r.ProviderRpcErrorCode = i;
    var a = (function (t) {
      return (
        (t[(t.Unknown = 0)] = "Unknown"),
        (t[(t.EVM = 1)] = "EVM"),
        (t[(t.Solana = 2)] = "Solana"),
        t
      );
    })({});
    r.ChainTypes = a;
  },
  function (t, r) {
    t.exports = function (t) {
      if ("function" != typeof t) throw TypeError(t + " is not a function!");
      return t;
    };
  },
  function (t, r, o) {
    t.exports = o(1458);
  },
  function (t, r, o) {
    var i = o(483),
      a = o(425).document,
      u = i(a) && i(a.createElement);
    t.exports = function (t) {
      return u ? a.createElement(t) : {};
    };
  },
  function (t, r, o) {
    var i = o(1126),
      a = o(426)("toStringTag"),
      u =
        "Arguments" ==
        i(
          (function () {
            return arguments;
          })()
        );
    t.exports = function (t) {
      var r, o, c;
      return void 0 === t
        ? "Undefined"
        : null === t
        ? "Null"
        : "string" ==
          typeof (o = (function (t, r) {
            try {
              return t[r];
            } catch (t) {}
          })((r = Object(t)), a))
        ? o
        : u
        ? i(r)
        : "Object" == (c = i(r)) && "function" == typeof r.callee
        ? "Arguments"
        : c;
    };
  },
  function (t, r, o) {
    var i = o(405),
      a = o(323),
      u = o(595);
    t.exports = function (t, r) {
      var o = (a.Object || {})[t] || Object[t],
        c = {};
      (c[t] = r(o)),
        i(
          i.S +
            i.F *
              u(function () {
                o(1);
              }),
          "Object",
          c
        );
    };
  },
  function (t, r, o) {
    "use strict";
    var i = o(425),
      a = o(524),
      u = o(427),
      c = o(405),
      l = o(1143),
      d = o(734).KEY,
      p = o(595),
      v = o(1132),
      h = o(1108),
      y = o(1111),
      _ = o(426),
      g = o(1112),
      b = o(1133),
      E = o(1431),
      m = o(1145),
      w = o(523),
      S = o(483),
      O = o(666),
      x = o(497),
      I = o(1131),
      P = o(721),
      T = o(1127),
      A = o(1435),
      R = o(1128),
      N = o(1116),
      L = o(434),
      C = o(667),
      k = R.f,
      M = L.f,
      j = A.f,
      U = i.Symbol,
      W = i.JSON,
      D = W && W.stringify,
      V = _("_hidden"),
      K = _("toPrimitive"),
      B = {}.propertyIsEnumerable,
      H = v("symbol-registry"),
      q = v("symbols"),
      z = v("op-symbols"),
      G = Object.prototype,
      Q = "function" == typeof U && !!N.f,
      X = i.QObject,
      Y = !X || !X.prototype || !X.prototype.findChild,
      J =
        u &&
        p(function () {
          return (
            7 !=
            T(
              M({}, "a", {
                get: function () {
                  return M(this, "a", {value: 7}).a;
                },
              })
            ).a
          );
        })
          ? function (t, r, o) {
              var i = k(G, r);
              i && delete G[r], M(t, r, o), i && t !== G && M(G, r, i);
            }
          : M,
      wrap = function (t) {
        var r = (q[t] = T(U.prototype));
        return (r._k = t), r;
      },
      $ =
        Q && "symbol" == typeof U.iterator
          ? function (t) {
              return "symbol" == typeof t;
            }
          : function (t) {
              return t instanceof U;
            },
      Z = function defineProperty(t, r, o) {
        return (
          t === G && Z(z, r, o),
          w(t),
          (r = I(r, !0)),
          w(o),
          a(q, r)
            ? (o.enumerable
                ? (a(t, V) && t[V][r] && (t[V][r] = !1),
                  (o = T(o, {enumerable: P(0, !1)})))
                : (a(t, V) || M(t, V, P(1, {})), (t[V][r] = !0)),
              J(t, r, o))
            : M(t, r, o)
        );
      },
      ee = function defineProperties(t, r) {
        w(t);
        for (var o, i = E((r = x(r))), a = 0, u = i.length; u > a; )
          Z(t, (o = i[a++]), r[o]);
        return t;
      },
      te = function propertyIsEnumerable(t) {
        var r = B.call(this, (t = I(t, !0)));
        return (
          !(this === G && a(q, t) && !a(z, t)) &&
          (!(r || !a(this, t) || !a(q, t) || (a(this, V) && this[V][t])) || r)
        );
      },
      ne = function getOwnPropertyDescriptor(t, r) {
        if (((t = x(t)), (r = I(r, !0)), t !== G || !a(q, r) || a(z, r))) {
          var o = k(t, r);
          return !o || !a(q, r) || (a(t, V) && t[V][r]) || (o.enumerable = !0), o;
        }
      },
      re = function getOwnPropertyNames(t) {
        for (var r, o = j(x(t)), i = [], u = 0; o.length > u; )
          a(q, (r = o[u++])) || r == V || r == d || i.push(r);
        return i;
      },
      oe = function getOwnPropertySymbols(t) {
        for (var r, o = t === G, i = j(o ? z : x(t)), u = [], c = 0; i.length > c; )
          !a(q, (r = i[c++])) || (o && !a(G, r)) || u.push(q[r]);
        return u;
      };
    Q ||
      ((U = function Symbol() {
        if (this instanceof U) throw TypeError("Symbol is not a constructor!");
        var t = y(arguments.length > 0 ? arguments[0] : void 0),
          $set = function (r) {
            this === G && $set.call(z, r),
              a(this, V) && a(this[V], t) && (this[V][t] = !1),
              J(this, t, P(1, r));
          };
        return u && Y && J(G, t, {configurable: !0, set: $set}), wrap(t);
      }),
      l(U.prototype, "toString", function toString() {
        return this._k;
      }),
      (R.f = ne),
      (L.f = Z),
      (o(1137).f = A.f = re),
      (o(728).f = te),
      (N.f = oe),
      u && !o(1107) && l(G, "propertyIsEnumerable", te, !0),
      (g.f = function (t) {
        return wrap(_(t));
      })),
      c(c.G + c.W + c.F * !Q, {Symbol: U});
    for (
      var ie =
          "hasInstance,isConcatSpreadable,iterator,match,replace,search,species,split,toPrimitive,toStringTag,unscopables".split(
            ","
          ),
        ae = 0;
      ie.length > ae;

    )
      _(ie[ae++]);
    for (var ue = C(_.store), ce = 0; ue.length > ce; ) b(ue[ce++]);
    c(c.S + c.F * !Q, "Symbol", {
      for: function (t) {
        return a(H, (t += "")) ? H[t] : (H[t] = U(t));
      },
      keyFor: function keyFor(t) {
        if (!$(t)) throw TypeError(t + " is not a symbol!");
        for (var r in H) if (H[r] === t) return r;
      },
      useSetter: function () {
        Y = !0;
      },
      useSimple: function () {
        Y = !1;
      },
    }),
      c(c.S + c.F * !Q, "Object", {
        create: function create(t, r) {
          return void 0 === r ? T(t) : ee(T(t), r);
        },
        defineProperty: Z,
        defineProperties: ee,
        getOwnPropertyDescriptor: ne,
        getOwnPropertyNames: re,
        getOwnPropertySymbols: oe,
      });
    var se = p(function () {
      N.f(1);
    });
    c(c.S + c.F * se, "Object", {
      getOwnPropertySymbols: function getOwnPropertySymbols(t) {
        return N.f(O(t));
      },
    }),
      W &&
        c(
          c.S +
            c.F *
              (!Q ||
                p(function () {
                  var t = U();
                  return (
                    "[null]" != D([t]) || "{}" != D({a: t}) || "{}" != D(Object(t))
                  );
                })),
          "JSON",
          {
            stringify: function stringify(t) {
              for (var r, o, i = [t], a = 1; arguments.length > a; )
                i.push(arguments[a++]);
              if (((o = r = i[1]), (S(r) || void 0 !== t) && !$(t)))
                return (
                  m(r) ||
                    (r = function (t, r) {
                      if (("function" == typeof o && (r = o.call(this, t, r)), !$(r)))
                        return r;
                    }),
                  (i[1] = r),
                  D.apply(W, i)
                );
            },
          }
        ),
      U.prototype[K] || o(525)(U.prototype, K, U.prototype.valueOf),
      h(U, "Symbol"),
      h(Math, "Math", !0),
      h(i.JSON, "JSON", !0);
  },
  function (t, r, o) {
    t.exports =
      !o(427) &&
      !o(595)(function () {
        return (
          7 !=
          Object.defineProperty(o(1381)("div"), "a", {
            get: function () {
              return 7;
            },
          }).a
        );
      });
  },
  function (t, r, o) {
    var i = o(524),
      a = o(497),
      u = o(1432)(!1),
      c = o(1135)("IE_PROTO");
    t.exports = function (t, r) {
      var o,
        l = a(t),
        d = 0,
        p = [];
      for (o in l) o != c && i(l, o) && p.push(o);
      for (; r.length > d; ) i(l, (o = r[d++])) && (~u(p, o) || p.push(o));
      return p;
    };
  },
  function (t, r) {
    t.exports = function (t, r) {
      return {value: r, done: !!t};
    };
  },
  function (t, r, o) {
    var i = o(523);
    t.exports = function (t, r, o, a) {
      try {
        return a ? r(i(o)[0], o[1]) : r(o);
      } catch (r) {
        var u = t.return;
        throw (void 0 !== u && i(u.call(t)), r);
      }
    };
  },
  function (t, r, o) {
    var i = o(722),
      a = o(426)("iterator"),
      u = Array.prototype;
    t.exports = function (t) {
      return void 0 !== t && (i.Array === t || u[a] === t);
    };
  },
  function (t, r, o) {
    var i = o(1382),
      a = o(426)("iterator"),
      u = o(722);
    t.exports = o(323).getIteratorMethod = function (t) {
      if (null != t) return t[a] || t["@@iterator"] || u[i(t)];
    };
  },
  function (t, r, o) {
    "use strict";
    var i = o(434),
      a = o(721);
    t.exports = function (t, r, o) {
      r in t ? i.f(t, r, a(0, o)) : (t[r] = o);
    };
  },
  function (t, r, o) {
    "use strict";
    var i = o(434).f,
      a = o(1127),
      u = o(1139),
      c = o(665),
      l = o(1140),
      d = o(723),
      p = o(1138),
      v = o(1387),
      h = o(1426),
      y = o(427),
      _ = o(734).fastKey,
      g = o(668),
      b = y ? "_s" : "size",
      getEntry = function (t, r) {
        var o,
          i = _(r);
        if ("F" !== i) return t._i[i];
        for (o = t._f; o; o = o.n) if (o.k == r) return o;
      };
    t.exports = {
      getConstructor: function (t, r, o, p) {
        var v = t(function (t, i) {
          l(t, v, r, "_i"),
            (t._t = r),
            (t._i = a(null)),
            (t._f = void 0),
            (t._l = void 0),
            (t[b] = 0),
            null != i && d(i, o, t[p], t);
        });
        return (
          u(v.prototype, {
            clear: function clear() {
              for (var t = g(this, r), o = t._i, i = t._f; i; i = i.n)
                (i.r = !0), i.p && (i.p = i.p.n = void 0), delete o[i.i];
              (t._f = t._l = void 0), (t[b] = 0);
            },
            delete: function (t) {
              var o = g(this, r),
                i = getEntry(o, t);
              if (i) {
                var a = i.n,
                  u = i.p;
                delete o._i[i.i],
                  (i.r = !0),
                  u && (u.n = a),
                  a && (a.p = u),
                  o._f == i && (o._f = a),
                  o._l == i && (o._l = u),
                  o[b]--;
              }
              return !!i;
            },
            forEach: function forEach(t) {
              g(this, r);
              for (
                var o, i = c(t, arguments.length > 1 ? arguments[1] : void 0, 3);
                (o = o ? o.n : this._f);

              )
                for (i(o.v, o.k, this); o && o.r; ) o = o.p;
            },
            has: function has(t) {
              return !!getEntry(g(this, r), t);
            },
          }),
          y &&
            i(v.prototype, "size", {
              get: function () {
                return g(this, r)[b];
              },
            }),
          v
        );
      },
      def: function (t, r, o) {
        var i,
          a,
          u = getEntry(t, r);
        return (
          u
            ? (u.v = o)
            : ((t._l = u =
                {i: (a = _(r, !0)), k: r, v: o, p: (i = t._l), n: void 0, r: !1}),
              t._f || (t._f = u),
              i && (i.n = u),
              t[b]++,
              "F" !== a && (t._i[a] = u)),
          t
        );
      },
      getEntry: getEntry,
      setStrong: function (t, r, o) {
        p(
          t,
          r,
          function (t, o) {
            (this._t = g(t, r)), (this._k = o), (this._l = void 0);
          },
          function () {
            for (var t = this, r = t._k, o = t._l; o && o.r; ) o = o.p;
            return t._t && (t._l = o = o ? o.n : t._t._f)
              ? v(0, "keys" == r ? o.k : "values" == r ? o.v : [o.k, o.v])
              : ((t._t = void 0), v(1));
          },
          o ? "entries" : "values",
          !o,
          !0
        ),
          h(r);
      },
    };
  },
  function (t, r, o) {
    var i = o(1382),
      a = o(1464);
    t.exports = function (t) {
      return function toJSON() {
        if (i(this) != t) throw TypeError(t + "#toJSON isn't generic");
        return a(this);
      };
    };
  },
  ,
  ,
  function (t, r, o) {
    "use strict";
    o(24), o(3), o(18), o(33), o(1);
    var i = o(527),
      a = o(495),
      u = o(591),
      c = o(590),
      l = o(664),
      d = o(1118),
      p = o(493);
    Object.defineProperty(r, "__esModule", {value: !0}),
      (r.create = void 0),
      o(118),
      o(25),
      o(66);
    var v = p(o(588)),
      h = p(o(1380)),
      y = o(1498),
      _ = o(1399),
      g = _interopRequireWildcard(o(1179)),
      b = _interopRequireWildcard(o(1401)),
      E = o(100),
      m = o(1418),
      w = o(1402),
      S = p(o(223));
    function _getRequireWildcardCache(t) {
      if ("function" != typeof d) return null;
      var r = new d(),
        o = new d();
      return (_getRequireWildcardCache = function _getRequireWildcardCache(t) {
        return t ? o : r;
      })(t);
    }
    function _interopRequireWildcard(t, r) {
      if (!r && t && t.__esModule) return t;
      if (null === t || ("object" !== i(t) && "function" != typeof t))
        return {default: t};
      var o = _getRequireWildcardCache(r);
      if (o && o.has(t)) return o.get(t);
      var a = {},
        u = Object.defineProperty && c;
      for (var l in t)
        if ("default" !== l && Object.prototype.hasOwnProperty.call(t, l)) {
          var d = u ? c(t, l) : null;
          d && (d.get || d.set) ? Object.defineProperty(a, l, d) : (a[l] = t[l]);
        }
      return (a.default = t), o && o.set(t, a), a;
    }
    function ownKeys(t, r) {
      var o = a(t);
      if (u) {
        var i = u(t);
        r &&
          (i = i.filter(function (r) {
            return c(t, r).enumerable;
          })),
          o.push.apply(o, i);
      }
      return o;
    }
    function _objectSpread(t) {
      for (var r = 1; r < arguments.length; r++) {
        var o = null != arguments[r] ? arguments[r] : {};
        r % 2
          ? ownKeys(Object(o), !0).forEach(function (r) {
              (0, v.default)(t, r, o[r]);
            })
          : l
          ? Object.defineProperties(t, l(o))
          : ownKeys(Object(o)).forEach(function (r) {
              Object.defineProperty(t, r, c(o, r));
            });
      }
      return t;
    }
    r.create = function create(t) {
      var r = arguments.length > 1 && void 0 !== arguments[1] ? arguments[1] : {};
      return (
        (r.detectedWeb3WalletIds = (0, m.getInstalledWalletPlugins)(
          r.web3ValidChains && r.web3ValidChains[0]
        )),
        (r.version = E.VERSION),
        (0, y.create)(t, r)
      );
    };
    (b.hooks.getConfig = function (t, r) {
      return (function getConfig(t) {
        var r = t.apiVersion,
          o = t.clientName,
          i = t.configUserId,
          a = t.configUserTags,
          u = t.countryCodes,
          c = t.customizations,
          l = t.depositSwitchToken,
          d = t.embeddedOpenLinkConfiguration,
          p = t.embeddedWorkflowSessionId,
          v = t.embeddedComponentConfiguration,
          h = t.env,
          y = t.experimentVariants,
          _ = t.forceDarkMode,
          b = t.hostedLinkVersion,
          E = t.institutionContactMessagingInstitutions,
          m = t.isEagerStart,
          w = t.isEmbedded,
          O = t.isPrivacyPortalItemAdd,
          x = t.isSimpleIntegration,
          I = t.isUsingWalletOnboardCallback,
          P = t.key,
          T = t.language,
          A = t.linkOpenId,
          R = t.linkCustomizationName,
          N = t.logInternalAnalytics,
          L = t.oauthNonce,
          C = t.oauthRedirectUri,
          k = t.oauthStateId,
          M = t.onEvent,
          j = t.onResult,
          U = t.onExit,
          W = t.onLoad,
          D = t.paymentToken,
          V = t.product,
          K = t.receivedRedirectUri,
          B = t.accountSubtypes,
          H = t.selectAccount,
          q = t.noLoadingState,
          z = t.token,
          G = t.useMockFingerprint,
          Q = t.user,
          X = t.userLegalName,
          Y = t.userEmailAddress,
          J = t.userPhoneNumber,
          $ = t.webhook,
          Z = t.workflowVersionOverride,
          ee = t.detectedWeb3WalletIds,
          te = t.web3ValidChains,
          ne = t.version;
        return {
          apiVersion: r,
          clientName: o,
          configUserId: i,
          configUserTags: a,
          countryCodes: u,
          customizations: c,
          depositSwitchToken: l,
          embeddedOpenLinkConfiguration: d,
          embeddedComponentConfiguration: v,
          embeddedWorkflowSessionId: p,
          env: h,
          experimentVariants: y,
          forceIframe: !0,
          forceDarkMode: _,
          hostedLinkVersion: b,
          institutionContactMessagingInstitutions: E,
          isPrivacyPortalItemAdd: O,
          isEagerStart: null != m && m,
          isEmbedded: w,
          isParentInlineStylesheetSupported: g.isInlineStylesheetSupported(),
          isParentMetaViewportSet: g.isMetaViewportSet(),
          isSimpleIntegration: !0 === x,
          isUsingOnEventCallback: "function" == typeof M,
          isUsingOnResultCallback: "function" == typeof j,
          isUsingOnExitCallback: "function" == typeof U,
          isUsingOnLoadCallback: "function" == typeof W,
          isUsingWalletOnboardCallback: I,
          key: P,
          language: T,
          linkCustomizationName: R,
          linkOpenId: null != A ? A : (0, S.default)(),
          logInternalAnalytics: !0 === N,
          oauthNonce: L,
          oauthRedirectUri: C,
          oauthStateId: k,
          parentMetaViewport: g.getMetaViewport(),
          paymentToken: D,
          product: V,
          receivedRedirectUri: K,
          accountSubtypes: B,
          selectAccount: !0 === H,
          noLoadingState: q,
          token: z,
          useMockFingerprint: G,
          user: Q,
          userLegalName: X,
          userEmailAddress: Y,
          userPhoneNumber: J,
          version: ne,
          webhook: $,
          workflowVersionOverride: Z,
          detectedWeb3WalletIds: ee,
          web3ValidChains: te,
          isLinkWebSdk: void 0,
          linkSdkVersion: void 0,
        };
      })(
        _objectSpread(
          _objectSpread({}, t),
          {},
          {
            isUsingWalletOnboardCallback: !!r.onProviderSuccess,
            workflowVersionOverride: r.workflowVersionOverride,
            detectedWeb3WalletIds: r.detectedWeb3WalletIds,
            isEagerStart: r.isEagerStart,
            version: r.version,
            web3ValidChains: r.web3ValidChains,
            forceDarkMode: r.forceDarkMode,
            embeddedWorkflowSessionId: r.embeddedWorkflowSessionId,
            embeddedOpenLinkConfiguration: r.embeddedOpenLinkConfiguration,
            useMockFingerprint: r.useMockFingerprint,
          }
        )
      );
    }),
      (b.hooks.getQueryParameters = function getQueryParameters(t) {
        var r = t.countryCodes,
          o = t.embeddedComponentConfiguration,
          i = t.env,
          a = t.experimentVariants,
          u = t.key,
          c = t.token,
          l = t.language,
          d = t.linkCustomizationName,
          p = t.origin,
          v = t.product,
          y = t.accountSubtypes,
          _ = t.uniqueId,
          g = t.oauthStateId,
          b = t.noLoadingState,
          E = t.version,
          m = t.hostedLinkVersion,
          w = t.linkOpenId;
        return {
          countryCodes: r,
          embeddedComponentConfiguration: null == o ? void 0 : (0, h.default)(o),
          env: i,
          experimentVariants: null == a ? void 0 : (0, h.default)(a),
          isLinkInitialize: !0,
          key: u,
          token: c,
          language: l,
          linkCustomizationName: d,
          origin: p,
          product: v,
          accountSubtypes: (0, h.default)(y),
          uniqueId: _,
          version: E,
          oauthStateId: g,
          noLoadingState: b,
          hostedLinkVersion: m,
          linkOpenId: w,
          isLinkWebSdk: void 0,
          linkSdkVersion: void 0,
        };
      }),
      (b.hooks.validateCreateOptions = w.validateCreateOptions),
      (b.hooks.updateLinkURL = function (t, r) {
        if ("1.1.0" === r.hostedLinkVersion) {
          if (-1 !== t.indexOf("cdn.plaid.com"))
            return t.replace("cdn.plaid.com", "secure.plaid.com");
          if (-1 !== t.indexOf("cdn-testing.plaid.com"))
            return t.replace("cdn-testing.plaid.com", "secure-testing.plaid.com");
        }
        return t;
      }),
      (b.hooks.emitLinkOpen = _.emitLinkOpen);
  },
  function (t, r, o) {
    "use strict";
    o(52), o(44), o(95), o(58), o(22), o(79), o(93), o(29), o(1), o(12);
    var i = o(2),
      a = o(11);
    Object.defineProperty(r, "__esModule", {value: !0}),
      (r.uuid =
        r.sendMessage =
        r.queryStringFromQueryParameters =
        r.getWindowOrigin =
        r.getUniqueId =
        r.default =
        r.createMessageEventListener =
        r.buildLinkUrl =
          void 0);
    var u = i(o(26));
    o(37), o(235), o(86), o(9), o(3), o(10), o(14), o(108), o(121), o(55), o(25), o(66);
    var c = (function _interopRequireWildcard(t, r) {
      if (!r && t && t.__esModule) return t;
      if (null === t || ("object" !== a(t) && "function" != typeof t))
        return {default: t};
      var o = _getRequireWildcardCache(r);
      if (o && o.has(t)) return o.get(t);
      var i = {},
        u = Object.defineProperty && Object.getOwnPropertyDescriptor;
      for (var c in t)
        if ("default" !== c && Object.prototype.hasOwnProperty.call(t, c)) {
          var l = u ? Object.getOwnPropertyDescriptor(t, c) : null;
          l && (l.get || l.set) ? Object.defineProperty(i, c, l) : (i[c] = t[c]);
        }
      (i.default = t), o && o.set(t, i);
      return i;
    })(o(231));
    function _getRequireWildcardCache(t) {
      if ("function" != typeof WeakMap) return null;
      var r = new WeakMap(),
        o = new WeakMap();
      return (_getRequireWildcardCache = function _getRequireWildcardCache(t) {
        return t ? o : r;
      })(t);
    }
    function _createForOfIteratorHelper(t, r) {
      var o = ("undefined" != typeof Symbol && t[Symbol.iterator]) || t["@@iterator"];
      if (!o) {
        if (
          Array.isArray(t) ||
          (o = (function _unsupportedIterableToArray(t, r) {
            if (!t) return;
            if ("string" == typeof t) return _arrayLikeToArray(t, r);
            var o = Object.prototype.toString.call(t).slice(8, -1);
            "Object" === o && t.constructor && (o = t.constructor.name);
            if ("Map" === o || "Set" === o) return Array.from(t);
            if ("Arguments" === o || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(o))
              return _arrayLikeToArray(t, r);
          })(t)) ||
          (r && t && "number" == typeof t.length)
        ) {
          o && (t = o);
          var i = 0,
            a = function F() {};
          return {
            s: a,
            n: function n() {
              return i >= t.length ? {done: !0} : {done: !1, value: t[i++]};
            },
            e: function e(t) {
              throw t;
            },
            f: a,
          };
        }
        throw new TypeError(
          "Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."
        );
      }
      var u,
        c = !0,
        l = !1;
      return {
        s: function s() {
          o = o.call(t);
        },
        n: function n() {
          var t = o.next();
          return (c = t.done), t;
        },
        e: function e(t) {
          (l = !0), (u = t);
        },
        f: function f() {
          try {
            c || null == o.return || o.return();
          } finally {
            if (l) throw u;
          }
        },
      };
    }
    function _arrayLikeToArray(t, r) {
      (null == r || r > t.length) && (r = t.length);
      for (var o = 0, i = new Array(r); o < r; o++) i[o] = t[o];
      return i;
    }
    r.buildLinkUrl = function buildLinkUrl(t) {
      var r = arguments.length > 1 && void 0 !== arguments[1] ? arguments[1] : c,
        o = p(t),
        i =
          r.LINK_CLIENT_STABLE_URL.length > 0
            ? r.LINK_CLIENT_STABLE_URL
            : r.LINK_CLIENT_URL,
        a = r.LINK_HTML_PATH;
      return "".concat(i).concat(a, "?").concat(o);
    };
    var l,
      d =
        ((l = 0),
        function () {
          return (l += 1), String(l);
        });
    r.getUniqueId = d;
    r.getWindowOrigin = function getWindowOrigin() {
      return null != window.location.origin
        ? window.location.origin
        : window.location.protocol +
            "//" +
            window.location.hostname +
            (window.location.port ? ":" + window.location.port : "");
    };
    r.sendMessage = function sendMessage(t) {
      var r = arguments.length > 1 && void 0 !== arguments[1] ? arguments[1] : void 0;
      return function (o) {
        var i = Object.assign({}, o, {
          action: "".concat(c.PLAID_INTERNAL_NAMESPACE, "::").concat(o.action),
        });
        t.postMessage(JSON.stringify(i), r || c.LINK_CLIENT_CORS_ORIGIN);
      };
    };
    r.createMessageEventListener = function createMessageEventListener(t, r, o) {
      return function (i) {
        var a = (function parseJSON(t) {
          try {
            return JSON.parse(t);
          } catch (t) {
            return {};
          }
        })(i.data);
        for (var u in o)
          if (a.action === "".concat(t, "-").concat(r, "::").concat(u)) return o[u](a);
      };
    };
    var p = function queryStringFromQueryParameters(t) {
      for (
        var r = new URLSearchParams(), o = 0, i = Object.entries(t);
        o < i.length;
        o++
      ) {
        var a = (0, u.default)(i[o], 2),
          c = a[0],
          l = a[1];
        if (null != l)
          if (Array.isArray(l)) {
            if (l.length > 0) {
              var d,
                p = _createForOfIteratorHelper(l);
              try {
                for (p.s(); !(d = p.n()).done; ) {
                  var v = d.value;
                  null != v && r.append(c, v);
                }
              } catch (t) {
                p.e(t);
              } finally {
                p.f();
              }
            }
          } else "boolean" == typeof l ? r.append(c, String(l)) : r.append(c, l);
      }
      return r.toString();
    };
    r.queryStringFromQueryParameters = p;
    var v = function uuid() {
      var t = window.crypto || window.msCrypto;
      return null != t && "randomUUID" in t
        ? t.randomUUID()
        : "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (t) {
            var r = (16 * Math.random()) | 0;
            return ("x" === t ? r : (3 & r) | 8).toString(16);
          });
    };
    r.uuid = v;
    var h = v;
    r.default = h;
  },
  function (t, r, o) {
    "use strict";
    o(1),
      Object.defineProperty(r, "__esModule", {value: !0}),
      (r.messageHandlerExtensions = r.hooks = void 0);
    r.messageHandlerExtensions = {};
    r.hooks = {
      getConfig: null,
      getQueryParameters: null,
      validateCreateOptions: null,
      updateLinkURL: null,
      emitLinkOpen: null,
    };
  },
  function (t, r, o) {
    "use strict";
    o(1),
      Object.defineProperty(r, "__esModule", {value: !0}),
      (r.emitLinkOpen = void 0);
    var i = o(231);
    r.emitLinkOpen = function emitLinkOpen(t) {
      var r = document.createElement("iframe");
      (r.id = "plaid-link-open-iframe"),
        (r.title = "Plaid Link Open"),
        (r.src = t),
        (r.allow = "camera ".concat(i.LINK_IFRAME_FEATURE_POLICY_URLS, ";")),
        r.setAttribute("sandbox", i.LINK_IFRAME_SANDBOX_PERMISSIONS),
        (r.width = "100%"),
        (r.height = "100%"),
        (r.style.position = "fixed"),
        (r.style.top = "0"),
        (r.style.left = "0"),
        (r.style.right = "0"),
        (r.style.bottom = "0"),
        (r.style.zIndex = "9999999999"),
        (r.style.borderWidth = "0"),
        (r.style.display = "none"),
        (r.style.overflowX = "hidden"),
        (r.style.overflowY = "auto"),
        (r.onload = function () {
          r.parentNode && r.parentNode.removeChild(r);
        }),
        document.body.appendChild(r);
    };
  },
  function (t, r, o) {
    "use strict";
    o(1);
    var i = o(2);
    Object.defineProperty(r, "__esModule", {value: !0}),
      (r.validateExitOptions = r.validateCreateOptions = void 0);
    var a = i(o(11));
    o(118);
    var u = o(231),
      c = function getValidationHandlers(t) {
        var r = t.env;
        return {
          error: function error(t) {
            if ("production" !== r) throw new Error(t);
          },
          warn: function warn(t) {
            "production" !== r && console.warn(t);
          },
        };
      };
    r.validateCreateOptions = function validateCreateOptions(t) {
      var r = c(t).error;
      !(function validateCreateKeys(t) {
        var r = c(t).warn;
        for (var o in t)
          u.CREATE_PARAMETERS.indexOf(o) < 0 &&
            r(
              "Invalid Link parameter: ".concat(
                o,
                " is not a valid Plaid.create() parameter"
              )
            );
      })(t),
        "function" != typeof t.onSuccess && r("Invalid onSuccess function"),
        null == t.receivedRedirectUri &&
          null == t.token &&
          r("Missing Link parameter. Link requires a token to be provided.");
    };
    r.validateExitOptions = function validateExitOptions(t, r) {
      var o = c(t).error;
      return (
        null == r ||
          ("object" !== (0, a.default)(r) &&
            o("Invalid exit parameter, must be an Object")),
        null
      );
    };
  },
  function (t, r, o) {
    "use strict";
    var i = o(495);
    o(1), o(3), o(18), Object.defineProperty(r, "__esModule", {value: !0});
    var a = o(1398);
    i(a).forEach(function (t) {
      "default" !== t &&
        "__esModule" !== t &&
        ((t in r && r[t] === a[t]) ||
          Object.defineProperty(r, t, {
            enumerable: !0,
            get: function get() {
              return a[t];
            },
          }));
    });
  },
  function (t, r, o) {
    "use strict";
    o(1),
      Object.defineProperty(r, "__esModule", {value: !0}),
      (r.validateEmbeddedComponentConfiguration = r.validateCreateOptions = void 0),
      o(118);
    var i = o(1180),
      a = function getValidationHandlers(t) {
        var r = t.env;
        return {
          error: function error(t) {
            if ("production" !== r) throw new Error(t);
          },
          warn: function warn(t) {
            "production" !== r && console.warn(t);
          },
        };
      };
    r.validateCreateOptions = function validateCreateOptions(t) {
      var r = a(t),
        o = r.error,
        u = r.warn;
      !(function validateCreateKeys(t) {
        var r = a(t).warn;
        for (var o in t)
          i.CREATE_PARAMETERS.indexOf(o) < 0 &&
            r(
              "Invalid Link parameter: ".concat(
                o,
                " is not a valid Plaid.create() parameter"
              )
            );
      })(t),
        "function" != typeof t.onSuccess && o("Invalid onSuccess function"),
        void 0 !== t.forceIframe &&
          u(
            "The forceIframe option has been deprecated. Link will use an iframe by default when possible."
          ),
        null == t.key &&
          null == t.token &&
          null == t.receivedRedirectUri &&
          o(
            "Missing Link parameter. Link requires a key, token, or received redirect URI to be provided."
          );
    };
    r.validateEmbeddedComponentConfiguration =
      function validateEmbeddedComponentConfiguration(t) {
        switch (null == t ? void 0 : t.type) {
          case "button":
            return {button_component_configuration: {}};
          case "mini_card":
            return {mini_card_component_configuration: {}};
          case "institution_select":
            return {institution_select_component_configuration: {}};
          case "chip":
            return {chip_component_configuration: {}};
        }
        return null;
      };
  },
  function (t, r) {
    (t.exports = function _arrayLikeToArray(t, r) {
      (null == r || r > t.length) && (r = t.length);
      for (var o = 0, i = new Array(r); o < r; o++) i[o] = t[o];
      return i;
    }),
      (t.exports.__esModule = !0),
      (t.exports.default = t.exports);
  },
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  function (t, r, o) {
    "use strict";
    o(1),
      Object.defineProperty(r, "__esModule", {value: !0}),
      (r.default = function determineChainTypeFromChainId(t) {
        var r = t.split(":");
        if (r.length < 2)
          return "0x" === t.substring(0, 2) ? i.ChainTypes.EVM : i.ChainTypes.Unknown;
        switch (r[0]) {
          case "solana":
            return i.ChainTypes.Solana;
          case "eip155":
          case "EIP155":
            return i.ChainTypes.EVM;
          default:
            return i.ChainTypes.Unknown;
        }
      });
    var i = o(1378);
  },
  ,
  function (t, r, o) {
    t.exports = o(1453);
  },
  function (t, r, o) {
    "use strict";
    var i = o(1117),
      a = o(1130),
      u = o(1146);
    o(52), o(44), o(25), o(58), o(1);
    var c = o(493);
    Object.defineProperty(r, "__esModule", {value: !0}),
      (r.getProviderByChainType =
        r.getInstalledWalletPlugins =
        r.getEIP1193ProviderByWalletBrandId =
          void 0);
    var l = c(o(527)),
      d = c(o(588)),
      p = c(o(1419)),
      v = c(o(1467)),
      h = c(o(1471)),
      y = c(o(1117));
    o(210), o(3), o(55), o(18), o(24), o(120);
    var _,
      g,
      b,
      E = o(1421),
      m = c(o(395)),
      w = o(1378),
      S = c(o(1415));
    function _createForOfIteratorHelper(t, r) {
      var o = (void 0 !== a && t[u]) || t["@@iterator"];
      if (!o) {
        if (
          Array.isArray(t) ||
          (o = (function _unsupportedIterableToArray(t, r) {
            if (!t) return;
            if ("string" == typeof t) return _arrayLikeToArray(t, r);
            var o = Object.prototype.toString.call(t).slice(8, -1);
            "Object" === o && t.constructor && (o = t.constructor.name);
            if ("Map" === o || "Set" === o) return i(t);
            if ("Arguments" === o || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(o))
              return _arrayLikeToArray(t, r);
          })(t)) ||
          (r && t && "number" == typeof t.length)
        ) {
          o && (t = o);
          var c = 0,
            l = function F() {};
          return {
            s: l,
            n: function n() {
              return c >= t.length ? {done: !0} : {done: !1, value: t[c++]};
            },
            e: function e(t) {
              throw t;
            },
            f: l,
          };
        }
        throw new TypeError(
          "Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."
        );
      }
      var d,
        p = !0,
        v = !1;
      return {
        s: function s() {
          o = o.call(t);
        },
        n: function n() {
          var t = o.next();
          return (p = t.done), t;
        },
        e: function e(t) {
          (v = !0), (d = t);
        },
        f: function f() {
          try {
            p || null == o.return || o.return();
          } finally {
            if (v) throw d;
          }
        },
      };
    }
    function _arrayLikeToArray(t, r) {
      (null == r || r > t.length) && (r = t.length);
      for (var o = 0, i = new Array(r); o < r; o++) i[o] = t[o];
      return i;
    }
    var O = [
        "isMetaMask",
        "isBraveWallet",
        "isCoinbaseWallet",
        "isCoinbaseBrowser",
        "isRabby",
        "__XDEFI",
        "isXDEFI",
        "isGamestop",
        "isBitKeep",
        "isBitKeepChrome",
        "isMathWallet",
        "isTokenary",
        "isTally",
        "isAlphaWallet",
        "isBitpie",
        "isBlockWallet",
        "isExodus",
        "isHbWallet",
        "isImToken",
        "isLiquality",
        "isTrust",
        "isTrustWallet",
        "isOneInchIOSWallet",
        "isOneInchAndroidWallet",
        "isTokenPocket",
        "isMEWwallet",
        "isSequence",
        "isDfox",
        "isDeficonnectProvider",
        "isPhantom",
        "isSolflare",
        "isGlow",
      ].sort(),
      x = new p.default(
        (0, v.default)(
          ((_ = {isMetaMask: "wallet_347"}),
          (0, d.default)(_, ["isBraveWallet", "isMetaMask"].toString(), "wallet_375"),
          (0, d.default)(_, ["isBraveWallet", "isPhantom"].toString(), "wallet_375"),
          (0, d.default)(_, ["__XDEFI", "isXDEFI"].toString(), "wallet_343"),
          (0, d.default)(_, ["__XDEFI", "isMetaMask"].toString(), "wallet_343"),
          (0, d.default)(_, ["isMetaMask", "isRabby"].toString(), "wallet_353"),
          (0, d.default)(
            _,
            ["isBitKeep", "isBitKeepChrome", "isMetaMask"].toString(),
            "wallet_354"
          ),
          (0, d.default)(_, ["isMathWallet", "isMetaMask"].toString(), "wallet_349"),
          (0, d.default)(_, ["isMetaMask", "isTokenary"].toString(), "wallet_351"),
          (0, d.default)(
            _,
            ["isDeficonnectProvider", "isMetaMask"].toString(),
            "wallet_356"
          ),
          (0, d.default)(_, "isCoinbaseWallet", "wallet_374"),
          (0, d.default)(_, "isGamestop", "wallet_344"),
          (0, d.default)(_, "isTally", "wallet_345"),
          (0, d.default)(_, "isBlockWallet", "wallet_340"),
          (0, d.default)(_, "isLiquality", "wallet_342"),
          (0, d.default)(
            _,
            ["isDfox", "isMetaMask", "isTokenPocket"].toString(),
            "wallet_348"
          ),
          (0, d.default)(_, ["isTrust", "isTrustWallet"].toString(), "wallet_355"),
          (0, d.default)(_, "isPhantom", "wallet_420"),
          (0, d.default)(_, ["isPhantom", "isGlow"].toString(), "wallet_411"),
          _)
        )
      ),
      I = [
        {
          walletId: "wallet_374",
          brandId: "wallet_236",
          providerPath: ["coinbaseWalletExtension"],
          injectedProviderChainType: w.ChainTypes.EVM,
        },
        {
          walletId: "wallet_432",
          brandId: "wallet_236",
          providerPath: ["coinbaseSolana"],
          injectedProviderChainType: w.ChainTypes.Solana,
        },
        {
          walletId: "wallet_345",
          brandId: "wallet_233",
          providerPath: ["tally"],
          injectedProviderChainType: w.ChainTypes.EVM,
        },
        {
          walletId: "wallet_347",
          brandId: "wallet_4",
          injectedProviderChainType: w.ChainTypes.EVM,
        },
        {
          walletId: "wallet_354",
          brandId: "wallet_126",
          providerPath: ["bitkeep", "ethereum"],
          injectedProviderChainType: w.ChainTypes.EVM,
        },
        {
          walletId: "wallet_344",
          brandId: "wallet_232",
          providerPath: ["gamestop"],
          injectedProviderChainType: w.ChainTypes.EVM,
        },
        {
          walletId: "wallet_343",
          brandId: "wallet_231",
          injectedProviderChainType: w.ChainTypes.EVM,
        },
        {
          walletId: "wallet_349",
          brandId: "wallet_13",
          injectedProviderChainType: w.ChainTypes.EVM,
        },
        {
          walletId: "wallet_348",
          brandId: "wallet_11",
          injectedProviderChainType: w.ChainTypes.EVM,
        },
        {
          walletId: "wallet_353",
          brandId: "wallet_70",
          injectedProviderChainType: w.ChainTypes.EVM,
        },
        {
          walletId: "wallet_340",
          brandId: "wallet_229",
          injectedProviderChainType: w.ChainTypes.EVM,
        },
        {
          walletId: "wallet_341",
          brandId: "wallet_129",
          providerPath: ["exodus", "ethereum"],
          injectedProviderChainType: w.ChainTypes.EVM,
        },
        {
          walletId: "wallet_342",
          brandId: "wallet_230",
          injectedProviderChainType: w.ChainTypes.EVM,
        },
        {
          walletId: "wallet_375",
          brandId: "wallet_237",
          injectedProviderChainType: w.ChainTypes.EVM,
        },
        {
          walletId: "wallet_375",
          brandId: "wallet_237",
          providerPath: ["braveSolana"],
          injectedProviderChainType: w.ChainTypes.Solana,
        },
        {
          walletId: "wallet_355",
          brandId: "wallet_2",
          providerPath: ["trustwallet"],
          injectedProviderChainType: w.ChainTypes.EVM,
        },
        {
          walletId: "wallet_355",
          brandId: "wallet_2",
          providerPath: ["trustwallet", "solana"],
          injectedProviderChainType: w.ChainTypes.Solana,
        },
        {
          walletId: "wallet_356",
          brandId: "wallet_6",
          providerPath: ["deficonnectProvider"],
          injectedProviderChainType: w.ChainTypes.EVM,
        },
        {
          walletId: "wallet_426",
          brandId: "wallet_273",
          providerPath: ["solflare"],
          injectedProviderChainType: w.ChainTypes.Solana,
        },
        {
          walletId: "wallet_411",
          brandId: "wallet_264",
          providerPath: ["glowSolana"],
          injectedProviderChainType: w.ChainTypes.Solana,
        },
      ],
      P = new p.default(
        (0, v.default)(
          ((g = {isMetaMask: "wallet_358", isCoinbaseWallet: "wallet_374"}),
          (0, d.default)(
            g,
            ["isCoinbaseBrowser", "isCoinbaseWallet"].toString(),
            "wallet_372"
          ),
          (0, d.default)(g, "isAlphaWallet", "wallet_364"),
          (0, d.default)(g, "isBitpie", "wallet_368"),
          (0, d.default)(g, "isHbWallet", "wallet_362"),
          (0, d.default)(g, "isImToken", "wallet_359"),
          (0, d.default)(g, "isTrust", "wallet_365"),
          (0, d.default)(
            g,
            ["isMetaMask", "isOneInchAndroidWallet", "isOneInchIOSWallet"].toString(),
            "wallet_361"
          ),
          (0, d.default)(g, ["isMathWallet", "isMetaMask"].toString(), "wallet_370"),
          (0, d.default)(g, ["isBitKeep", "isMetaMask"].toString(), "wallet_371"),
          (0, d.default)(
            g,
            ["isMetaMask", "isTokenPocket", "isTrust"].toString(),
            "wallet_360"
          ),
          (0, d.default)(
            g,
            ["isMEWwallet", "isMetaMask", "isTrust"].toString(),
            "wallet_376"
          ),
          (0, d.default)(g, "isPhantom", "wallet_433"),
          g)
        )
      ),
      T = new p.default(
        (0, v.default)(
          ((b = {}),
          (0, d.default)(b, w.ChainTypes.EVM, function () {
            return window.ethereum;
          }),
          (0, d.default)(b, w.ChainTypes.Solana, function () {
            return window.solana;
          }),
          b)
        )
      ),
      A = function getProviderByChainType(t) {
        var r = T.get(t.toString());
        if (void 0 !== r) return r();
      };
    r.getProviderByChainType = A;
    r.getInstalledWalletPlugins = function getInstalledWalletPlugins(t) {
      var r = new h.default(),
        o = t ? (0, S.default)(t) : w.ChainTypes.EVM,
        i = (0, m.default)().isMobile;
      i ||
        I.forEach(function (t) {
          N(t) && t.injectedProviderChainType === o && r.add(t.walletId);
        });
      var a = A(o);
      if (a) {
        var u,
          c = _createForOfIteratorHelper(null != a && a.providers ? a.providers : [a]);
        try {
          var l = function _loop() {
            var t = u.value,
              o = [];
            O.forEach(function (r) {
              !0 === t[r] && o.push(r);
            });
            var a = i ? P.get(o.toString()) : x.get(o.toString());
            (a && r.has(a)) ||
              r.add(
                a ||
                  (i ? E.UnidentifiedMobileBrowserWallet : E.UnidentifiedPluginWallet)
              );
          };
          for (c.s(); !(u = c.n()).done; ) l();
        } catch (t) {
          c.e(t);
        } finally {
          c.f();
        }
      }
      return (
        r.size > 1 && r.delete("wallet_353"),
        r.size > 1 &&
          (r.delete(E.UnidentifiedMobileBrowserWallet),
          r.delete(E.UnidentifiedPluginWallet)),
        (0, y.default)(r)
      );
    };
    r.getEIP1193ProviderByWalletBrandId = function getEIP1193ProviderByWalletBrandId(
      t
    ) {
      var r = I.filter(function (r) {
          return r.brandId === t;
        }),
        o = (0, m.default)().isMobile;
      return 1 !== r.length || o ? window.ethereum : R(r[0]);
    };
    var R = function getEIP1193ProviderFromProviderPath(t) {
        var r = window.ethereum;
        if (t.providerPath || r) {
          if (t.providerPath) {
            var o = N(t);
            return o || void 0;
          }
          if (r) {
            var i,
              a = _createForOfIteratorHelper(r.providers ? r.providers : [r]);
            try {
              var u = function _loop2() {
                var r = i.value,
                  o = [];
                if (
                  (O.forEach(function (t) {
                    !0 === r[t] && o.push(t);
                  }),
                  x.get(o.toString()) === t.walletId)
                )
                  return {v: r};
              };
              for (a.s(); !(i = a.n()).done; ) {
                var c = u();
                if ("object" === (0, l.default)(c)) return c.v;
              }
            } catch (t) {
              a.e(t);
            } finally {
              a.f();
            }
          }
        }
      },
      N = function findProvider(t) {
        var r;
        return null == t || null === (r = t.providerPath) || void 0 === r
          ? void 0
          : r.reduce(function (t, r) {
              if (t) return t[r];
            }, window);
      };
  },
  function (t, r, o) {
    t.exports = o(1461);
  },
  function (t, r, o) {
    var i = o(524),
      a = o(666),
      u = o(1135)("IE_PROTO"),
      c = Object.prototype;
    t.exports =
      Object.getPrototypeOf ||
      function (t) {
        return (
          (t = a(t)),
          i(t, u)
            ? t[u]
            : "function" == typeof t.constructor && t instanceof t.constructor
            ? t.constructor.prototype
            : t instanceof Object
            ? c
            : null
        );
      };
  },
  function (t, r, o) {
    "use strict";
    o(1),
      Object.defineProperty(r, "__esModule", {value: !0}),
      (r.WalletConnectBrand =
        r.UnidentifiedWalletBrand =
        r.UnidentifiedPluginWallet =
        r.UnidentifiedMobileBrowserWallet =
        r.TrustWalletBrandId =
          void 0);
    r.UnidentifiedWalletBrand = "wallet_240";
    r.UnidentifiedMobileBrowserWallet = "wallet_380";
    r.UnidentifiedPluginWallet = "wallet_381";
    r.WalletConnectBrand = "wallet_235";
    r.TrustWalletBrandId = "wallet_2";
  },
  ,
  function (t, r, o) {
    var i = o(425).document;
    t.exports = i && i.documentElement;
  },
  function (t, r, o) {
    var i = o(527).default,
      a = o(1455);
    (t.exports = function _toPropertyKey(t) {
      var r = a(t, "string");
      return "symbol" === i(r) ? r : String(r);
    }),
      (t.exports.__esModule = !0),
      (t.exports.default = t.exports);
  },
  function (t, r, o) {
    var i = o(426)("iterator"),
      a = !1;
    try {
      var u = [7][i]();
      (u.return = function () {
        a = !0;
      }),
        Array.from(u, function () {
          throw 2;
        });
    } catch (t) {}
    t.exports = function (t, r) {
      if (!r && !a) return !1;
      var o = !1;
      try {
        var u = [7],
          c = u[i]();
        (c.next = function () {
          return {done: (o = !0)};
        }),
          (u[i] = function () {
            return c;
          }),
          t(u);
      } catch (t) {}
      return o;
    };
  },
  function (t, r, o) {
    "use strict";
    var i = o(425),
      a = o(323),
      u = o(434),
      c = o(427),
      l = o(426)("species");
    t.exports = function (t) {
      var r = "function" == typeof a[t] ? a[t] : i[t];
      c &&
        r &&
        !r[l] &&
        u.f(r, l, {
          configurable: !0,
          get: function () {
            return this;
          },
        });
    };
  },
  ,
  ,
  ,
  function (t, r, o) {
    o(1384), o(1114), o(1436), o(1437), (t.exports = o(323).Symbol);
  },
  function (t, r, o) {
    var i = o(667),
      a = o(1116),
      u = o(728);
    t.exports = function (t) {
      var r = i(t),
        o = a.f;
      if (o)
        for (var c, l = o(t), d = u.f, p = 0; l.length > p; )
          d.call(t, (c = l[p++])) && r.push(c);
      return r;
    };
  },
  function (t, r, o) {
    var i = o(497),
      a = o(1113),
      u = o(1433);
    t.exports = function (t) {
      return function (r, o, c) {
        var l,
          d = i(r),
          p = a(d.length),
          v = u(c, p);
        if (t && o != o) {
          for (; p > v; ) if ((l = d[v++]) != l) return !0;
        } else for (; p > v; v++) if ((t || v in d) && d[v] === o) return t || v || 0;
        return !t && -1;
      };
    };
  },
  function (t, r, o) {
    var i = o(1134),
      a = Math.max,
      u = Math.min;
    t.exports = function (t, r) {
      return (t = i(t)) < 0 ? a(t + r, 0) : u(t, r);
    };
  },
  function (t, r, o) {
    var i = o(434),
      a = o(523),
      u = o(667);
    t.exports = o(427)
      ? Object.defineProperties
      : function defineProperties(t, r) {
          a(t);
          for (var o, c = u(r), l = c.length, d = 0; l > d; )
            i.f(t, (o = c[d++]), r[o]);
          return t;
        };
  },
  function (t, r, o) {
    var i = o(497),
      a = o(1137).f,
      u = {}.toString,
      c =
        "object" == typeof window && window && Object.getOwnPropertyNames
          ? Object.getOwnPropertyNames(window)
          : [];
    t.exports.f = function getOwnPropertyNames(t) {
      return c && "[object Window]" == u.call(t)
        ? (function (t) {
            try {
              return a(t);
            } catch (t) {
              return c.slice();
            }
          })(t)
        : a(i(t));
    };
  },
  function (t, r, o) {
    o(1133)("asyncIterator");
  },
  function (t, r, o) {
    o(1133)("observable");
  },
  function (t, r, o) {
    o(1109), o(1115), (t.exports = o(1112).f("iterator"));
  },
  function (t, r, o) {
    var i = o(1134),
      a = o(1129);
    t.exports = function (t) {
      return function (r, o) {
        var u,
          c,
          l = String(a(r)),
          d = i(o),
          p = l.length;
        return d < 0 || d >= p
          ? t
            ? ""
            : void 0
          : (u = l.charCodeAt(d)) < 55296 ||
            u > 56319 ||
            d + 1 === p ||
            (c = l.charCodeAt(d + 1)) < 56320 ||
            c > 57343
          ? t
            ? l.charAt(d)
            : u
          : t
          ? l.slice(d, d + 2)
          : c - 56320 + ((u - 55296) << 10) + 65536;
      };
    };
  },
  function (t, r, o) {
    "use strict";
    var i = o(1127),
      a = o(721),
      u = o(1108),
      c = {};
    o(525)(c, o(426)("iterator"), function () {
      return this;
    }),
      (t.exports = function (t, r, o) {
        (t.prototype = i(c, {next: a(1, o)})), u(t, r + " Iterator");
      });
  },
  function (t, r, o) {
    "use strict";
    var i = o(1442),
      a = o(1387),
      u = o(722),
      c = o(497);
    (t.exports = o(1138)(
      Array,
      "Array",
      function (t, r) {
        (this._t = c(t)), (this._i = 0), (this._k = r);
      },
      function () {
        var t = this._t,
          r = this._k,
          o = this._i++;
        return !t || o >= t.length
          ? ((this._t = void 0), a(1))
          : a(0, "keys" == r ? o : "values" == r ? t[o] : [o, t[o]]);
      },
      "values"
    )),
      (u.Arguments = u.Array),
      i("keys"),
      i("values"),
      i("entries");
  },
  function (t, r) {
    t.exports = function () {};
  },
  function (t, r, o) {
    var i = o(1444);
    t.exports = function (t, r) {
      return new (i(t))(r);
    };
  },
  function (t, r, o) {
    var i = o(483),
      a = o(1145),
      u = o(426)("species");
    t.exports = function (t) {
      var r;
      return (
        a(t) &&
          ("function" != typeof (r = t.constructor) ||
            (r !== Array && !a(r.prototype)) ||
            (r = void 0),
          i(r) && null === (r = r[u]) && (r = void 0)),
        void 0 === r ? Array : r
      );
    };
  },
  function (t, r, o) {
    o(1446);
    var i = o(323).Object;
    t.exports = function getOwnPropertyDescriptor(t, r) {
      return i.getOwnPropertyDescriptor(t, r);
    };
  },
  function (t, r, o) {
    var i = o(497),
      a = o(1128).f;
    o(1383)("getOwnPropertyDescriptor", function () {
      return function getOwnPropertyDescriptor(t, r) {
        return a(i(t), r);
      };
    });
  },
  function (t, r, o) {
    o(1448), (t.exports = o(323).Object.keys);
  },
  function (t, r, o) {
    var i = o(666),
      a = o(667);
    o(1383)("keys", function () {
      return function keys(t) {
        return a(i(t));
      };
    });
  },
  function (t, r, o) {
    o(1384), (t.exports = o(323).Object.getOwnPropertySymbols);
  },
  function (t, r, o) {
    o(1451), (t.exports = o(323).Object.getOwnPropertyDescriptors);
  },
  function (t, r, o) {
    var i = o(405),
      a = o(1452),
      u = o(497),
      c = o(1128),
      l = o(1391);
    i(i.S, "Object", {
      getOwnPropertyDescriptors: function getOwnPropertyDescriptors(t) {
        for (var r, o, i = u(t), d = c.f, p = a(i), v = {}, h = 0; p.length > h; )
          void 0 !== (o = d(i, (r = p[h++]))) && l(v, r, o);
        return v;
      },
    });
  },
  function (t, r, o) {
    var i = o(1137),
      a = o(1116),
      u = o(523),
      c = o(425).Reflect;
    t.exports =
      (c && c.ownKeys) ||
      function ownKeys(t) {
        var r = i.f(u(t)),
          o = a.f;
        return o ? r.concat(o(t)) : r;
      };
  },
  function (t, r, o) {
    o(1454);
    var i = o(323).Object;
    t.exports = function defineProperty(t, r, o) {
      return i.defineProperty(t, r, o);
    };
  },
  function (t, r, o) {
    var i = o(405);
    i(i.S + i.F * !o(427), "Object", {defineProperty: o(434).f});
  },
  function (t, r, o) {
    var i = o(1456),
      a = o(527).default;
    (t.exports = function _toPrimitive(t, r) {
      if ("object" !== a(t) || null === t) return t;
      var o = t[i];
      if (void 0 !== o) {
        var u = o.call(t, r || "default");
        if ("object" !== a(u)) return u;
        throw new TypeError("@@toPrimitive must return a primitive value.");
      }
      return ("string" === r ? String : Number)(t);
    }),
      (t.exports.__esModule = !0),
      (t.exports.default = t.exports);
  },
  function (t, r, o) {
    t.exports = o(1457);
  },
  function (t, r, o) {
    t.exports = o(1112).f("toPrimitive");
  },
  function (t, r, o) {
    var i = o(323),
      a = i.JSON || (i.JSON = {stringify: JSON.stringify});
    t.exports = function stringify(t) {
      return a.stringify.apply(a, arguments);
    };
  },
  function (t, r, o) {
    o(1109), o(1460), (t.exports = o(323).Array.from);
  },
  function (t, r, o) {
    "use strict";
    var i = o(665),
      a = o(405),
      u = o(666),
      c = o(1388),
      l = o(1389),
      d = o(1113),
      p = o(1391),
      v = o(1390);
    a(
      a.S +
        a.F *
          !o(1425)(function (t) {
            Array.from(t);
          }),
      "Array",
      {
        from: function from(t) {
          var r,
            o,
            a,
            h,
            y = u(t),
            _ = "function" == typeof this ? this : Array,
            g = arguments.length,
            b = g > 1 ? arguments[1] : void 0,
            E = void 0 !== b,
            m = 0,
            w = v(y);
          if (
            (E && (b = i(b, g > 2 ? arguments[2] : void 0, 2)),
            null == w || (_ == Array && l(w)))
          )
            for (o = new _((r = d(y.length))); r > m; m++)
              p(o, m, E ? b(y[m], m) : y[m]);
          else
            for (h = w.call(y), o = new _(); !(a = h.next()).done; m++)
              p(o, m, E ? c(h, b, [a.value, m], !0) : a.value);
          return (o.length = m), o;
        },
      }
    );
  },
  function (t, r, o) {
    o(1114),
      o(1109),
      o(1115),
      o(1462),
      o(1463),
      o(1465),
      o(1466),
      (t.exports = o(323).Map);
  },
  function (t, r, o) {
    "use strict";
    var i = o(1392),
      a = o(668),
      u = "Map";
    t.exports = o(1147)(
      u,
      function (t) {
        return function Map() {
          return t(this, arguments.length > 0 ? arguments[0] : void 0);
        };
      },
      {
        get: function get(t) {
          var r = i.getEntry(a(this, u), t);
          return r && r.v;
        },
        set: function set(t, r) {
          return i.def(a(this, u), 0 === t ? 0 : t, r);
        },
      },
      i,
      !0
    );
  },
  function (t, r, o) {
    var i = o(405);
    i(i.P + i.R, "Map", {toJSON: o(1393)("Map")});
  },
  function (t, r, o) {
    var i = o(723);
    t.exports = function (t, r) {
      var o = [];
      return i(t, !1, o.push, o, r), o;
    };
  },
  function (t, r, o) {
    o(1148)("Map");
  },
  function (t, r, o) {
    o(1149)("Map");
  },
  function (t, r, o) {
    t.exports = o(1468);
  },
  function (t, r, o) {
    o(1469), (t.exports = o(323).Object.entries);
  },
  function (t, r, o) {
    var i = o(405),
      a = o(1470)(!0);
    i(i.S, "Object", {
      entries: function entries(t) {
        return a(t);
      },
    });
  },
  function (t, r, o) {
    var i = o(427),
      a = o(667),
      u = o(497),
      c = o(728).f;
    t.exports = function (t) {
      return function (r) {
        for (var o, l = u(r), d = a(l), p = d.length, v = 0, h = []; p > v; )
          (o = d[v++]), (i && !c.call(l, o)) || h.push(t ? [o, l[o]] : l[o]);
        return h;
      };
    };
  },
  function (t, r, o) {
    t.exports = o(1472);
  },
  function (t, r, o) {
    o(1114),
      o(1109),
      o(1115),
      o(1473),
      o(1474),
      o(1475),
      o(1476),
      (t.exports = o(323).Set);
  },
  function (t, r, o) {
    "use strict";
    var i = o(1392),
      a = o(668);
    t.exports = o(1147)(
      "Set",
      function (t) {
        return function Set() {
          return t(this, arguments.length > 0 ? arguments[0] : void 0);
        };
      },
      {
        add: function add(t) {
          return i.def(a(this, "Set"), (t = 0 === t ? 0 : t), t);
        },
      },
      i
    );
  },
  function (t, r, o) {
    var i = o(405);
    i(i.P + i.R, "Set", {toJSON: o(1393)("Set")});
  },
  function (t, r, o) {
    o(1148)("Set");
  },
  function (t, r, o) {
    o(1149)("Set");
  },
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  ,
  function (t, r, o) {
    t.exports = o(1490);
  },
  function (t, r, o) {
    "use strict";
    o(1);
    var i = o(527),
      a = o(1118),
      u = o(590),
      c = o(493);
    Object.defineProperty(r, "__esModule", {value: !0}),
      (r.default = r.Plaid = void 0),
      o(1497);
    var l = o(1396),
      d = _interopRequireWildcard(o(1509)),
      p = _interopRequireWildcard(o(1510)),
      v = _interopRequireWildcard(o(1511)),
      h = _interopRequireWildcard(o(1401)),
      y = o(1180),
      _ = o(100),
      g = c(o(1512)),
      b = o(1515);
    function _getRequireWildcardCache(t) {
      if ("function" != typeof a) return null;
      var r = new a(),
        o = new a();
      return (_getRequireWildcardCache = function _getRequireWildcardCache(t) {
        return t ? o : r;
      })(t);
    }
    function _interopRequireWildcard(t, r) {
      if (!r && t && t.__esModule) return t;
      if (null === t || ("object" !== i(t) && "function" != typeof t))
        return {default: t};
      var o = _getRequireWildcardCache(r);
      if (o && o.has(t)) return o.get(t);
      var a = {},
        c = Object.defineProperty && u;
      for (var l in t)
        if ("default" !== l && Object.prototype.hasOwnProperty.call(t, l)) {
          var d = c ? u(t, l) : null;
          d && (d.get || d.set) ? Object.defineProperty(a, l, d) : (a[l] = t[l]);
        }
      return (a.default = t), o && o.set(t, a), a;
    }
    (h.messageHandlerExtensions[y.PLAID_INTERNAL_NAMESPACE] = []),
      h.messageHandlerExtensions[y.PLAID_INTERNAL_NAMESPACE].push(g.default),
      h.messageHandlerExtensions[y.PLAID_INTERNAL_NAMESPACE].push(
        d.extendMessageHandlers
      ),
      h.messageHandlerExtensions[y.PLAID_INTERNAL_NAMESPACE].push(
        v.extendMessageHandlers
      ),
      (h.messageHandlerExtensions[_.PLAID_FLOW_INTERNAL_NAMESPACE] = []),
      h.messageHandlerExtensions[_.PLAID_FLOW_INTERNAL_NAMESPACE].push(
        p.extendMessageHandlers
      );
    var E = {version: _.VERSION, create: l.create, createEmbedded: b.createEmbedded};
    (r.Plaid = E),
      void 0 !== window.Plaid &&
        console.warn(
          "Warning: The Plaid link-initialize.js script was embedded more than once. This is an unsupported configuration and may lead to unpredictable behavior. Please ensure Plaid Link is embedded only once per page."
        ),
      (window.Plaid = E);
    var m = d.findScriptTag();
    d.setUp(E, m), (t.exports = E);
    var w = E;
    r.default = w;
  },
  function (t, r, o) {
    o(1114), o(1115), o(1492), o(1495), o(1496), (t.exports = o(323).WeakMap);
  },
  function (t, r, o) {
    "use strict";
    var i,
      a = o(425),
      u = o(1158)(0),
      c = o(1143),
      l = o(734),
      d = o(1493),
      p = o(1494),
      v = o(483),
      h = o(668),
      y = o(668),
      _ = !a.ActiveXObject && "ActiveXObject" in a,
      g = "WeakMap",
      b = l.getWeak,
      E = Object.isExtensible,
      m = p.ufstore,
      wrapper = function (t) {
        return function WeakMap() {
          return t(this, arguments.length > 0 ? arguments[0] : void 0);
        };
      },
      w = {
        get: function get(t) {
          if (v(t)) {
            var r = b(t);
            return !0 === r ? m(h(this, g)).get(t) : r ? r[this._i] : void 0;
          }
        },
        set: function set(t, r) {
          return p.def(h(this, g), t, r);
        },
      },
      S = (t.exports = o(1147)(g, wrapper, w, p, !0, !0));
    y &&
      _ &&
      (d((i = p.getConstructor(wrapper, g)).prototype, w),
      (l.NEED = !0),
      u(["delete", "has", "get", "set"], function (t) {
        var r = S.prototype,
          o = r[t];
        c(r, t, function (r, a) {
          if (v(r) && !E(r)) {
            this._f || (this._f = new i());
            var u = this._f[t](r, a);
            return "set" == t ? this : u;
          }
          return o.call(this, r, a);
        });
      }));
  },
  function (t, r, o) {
    "use strict";
    var i = o(427),
      a = o(667),
      u = o(1116),
      c = o(728),
      l = o(666),
      d = o(1144),
      p = Object.assign;
    t.exports =
      !p ||
      o(595)(function () {
        var t = {},
          r = {},
          o = Symbol(),
          i = "abcdefghijklmnopqrst";
        return (
          (t[o] = 7),
          i.split("").forEach(function (t) {
            r[t] = t;
          }),
          7 != p({}, t)[o] || Object.keys(p({}, r)).join("") != i
        );
      })
        ? function assign(t, r) {
            for (var o = l(t), p = arguments.length, v = 1, h = u.f, y = c.f; p > v; )
              for (
                var _,
                  g = d(arguments[v++]),
                  b = h ? a(g).concat(h(g)) : a(g),
                  E = b.length,
                  m = 0;
                E > m;

              )
                (_ = b[m++]), (i && !y.call(g, _)) || (o[_] = g[_]);
            return o;
          }
        : p;
  },
  function (t, r, o) {
    "use strict";
    var i = o(1139),
      a = o(734).getWeak,
      u = o(523),
      c = o(483),
      l = o(1140),
      d = o(723),
      p = o(1158),
      v = o(524),
      h = o(668),
      y = p(5),
      _ = p(6),
      g = 0,
      uncaughtFrozenStore = function (t) {
        return t._l || (t._l = new UncaughtFrozenStore());
      },
      UncaughtFrozenStore = function () {
        this.a = [];
      },
      findUncaughtFrozen = function (t, r) {
        return y(t.a, function (t) {
          return t[0] === r;
        });
      };
    (UncaughtFrozenStore.prototype = {
      get: function (t) {
        var r = findUncaughtFrozen(this, t);
        if (r) return r[1];
      },
      has: function (t) {
        return !!findUncaughtFrozen(this, t);
      },
      set: function (t, r) {
        var o = findUncaughtFrozen(this, t);
        o ? (o[1] = r) : this.a.push([t, r]);
      },
      delete: function (t) {
        var r = _(this.a, function (r) {
          return r[0] === t;
        });
        return ~r && this.a.splice(r, 1), !!~r;
      },
    }),
      (t.exports = {
        getConstructor: function (t, r, o, u) {
          var p = t(function (t, i) {
            l(t, p, r, "_i"),
              (t._t = r),
              (t._i = g++),
              (t._l = void 0),
              null != i && d(i, o, t[u], t);
          });
          return (
            i(p.prototype, {
              delete: function (t) {
                if (!c(t)) return !1;
                var o = a(t);
                return !0 === o
                  ? uncaughtFrozenStore(h(this, r)).delete(t)
                  : o && v(o, this._i) && delete o[this._i];
              },
              has: function has(t) {
                if (!c(t)) return !1;
                var o = a(t);
                return !0 === o
                  ? uncaughtFrozenStore(h(this, r)).has(t)
                  : o && v(o, this._i);
              },
            }),
            p
          );
        },
        def: function (t, r, o) {
          var i = a(u(r), !0);
          return !0 === i ? uncaughtFrozenStore(t).set(r, o) : (i[t._i] = o), t;
        },
        ufstore: uncaughtFrozenStore,
      });
  },
  function (t, r, o) {
    o(1148)("WeakMap");
  },
  function (t, r, o) {
    o(1149)("WeakMap");
  },
  function (t, r, o) {
    "use strict";
    var i = o(100);
    o.p = i.LINK_CLIENT_URL + "/";
  },
  function (t, r, o) {
    "use strict";
    o(21), o(22), o(24), o(12), o(35), o(33), o(1), o(9), o(10), o(29), o(14);
    var i = o(2),
      a = o(11);
    Object.defineProperty(r, "__esModule", {value: !0}),
      (r.create = void 0),
      o(86),
      o(121),
      o(3),
      o(18);
    var u = i(o(26)),
      c = i(o(8)),
      l = _interopRequireWildcard(o(1499)),
      d = _interopRequireWildcard(o(1500)),
      p = _interopRequireWildcard(o(1397)),
      v = _interopRequireWildcard(o(1398)),
      h = o(231),
      y = i(o(400)),
      _ = i(o(417)),
      g = o(1399),
      b = o(1400);
    function _getRequireWildcardCache(t) {
      if ("function" != typeof WeakMap) return null;
      var r = new WeakMap(),
        o = new WeakMap();
      return (_getRequireWildcardCache = function _getRequireWildcardCache(t) {
        return t ? o : r;
      })(t);
    }
    function _interopRequireWildcard(t, r) {
      if (!r && t && t.__esModule) return t;
      if (null === t || ("object" !== a(t) && "function" != typeof t))
        return {default: t};
      var o = _getRequireWildcardCache(r);
      if (o && o.has(t)) return o.get(t);
      var i = {},
        u = Object.defineProperty && Object.getOwnPropertyDescriptor;
      for (var c in t)
        if ("default" !== c && Object.prototype.hasOwnProperty.call(t, c)) {
          var l = u ? Object.getOwnPropertyDescriptor(t, c) : null;
          l && (l.get || l.set) ? Object.defineProperty(i, c, l) : (i[c] = t[c]);
        }
      return (i.default = t), o && o.set(t, i), i;
    }
    function ownKeys(t, r) {
      var o = Object.keys(t);
      if (Object.getOwnPropertySymbols) {
        var i = Object.getOwnPropertySymbols(t);
        r &&
          (i = i.filter(function (r) {
            return Object.getOwnPropertyDescriptor(t, r).enumerable;
          })),
          o.push.apply(o, i);
      }
      return o;
    }
    function _objectSpread(t) {
      for (var r = 1; r < arguments.length; r++) {
        var o = null != arguments[r] ? arguments[r] : {};
        r % 2
          ? ownKeys(Object(o), !0).forEach(function (r) {
              (0, c.default)(t, r, o[r]);
            })
          : Object.getOwnPropertyDescriptors
          ? Object.defineProperties(t, Object.getOwnPropertyDescriptors(o))
          : ownKeys(Object(o)).forEach(function (r) {
              Object.defineProperty(t, r, Object.getOwnPropertyDescriptor(o, r));
            });
      }
      return t;
    }
    r.create = function create(t) {
      var r = arguments.length > 1 && void 0 !== arguments[1] ? arguments[1] : {};
      null != v.hooks.validateCreateOptions
        ? v.hooks.validateCreateOptions(t)
        : (0, b.validateCreateOptions)(t);
      var o = Date.now(),
        i = !0 === r.forceDesktop,
        a = !0 === r.forceMobile,
        c = (!i && (0, y.default)().isMobile) || a,
        E = p.getUniqueId(),
        m = (c ? d : l).create(),
        w = _objectSpread({}, t);
      delete w.onEvent, delete w.onExit, delete w.onLoad, delete w.onSuccess;
      var S = _objectSpread(
          {
            isMobile: c,
            uniqueId: E,
            linkOpenId: p.uuid(),
            origin: p.getWindowOrigin(),
            linkSdkVersion: h.LINK_WEB_SDK_VERSION,
            isLinkWebSdk: !0,
          },
          null == v.hooks.getConfig ? w : v.hooks.getConfig(t, r)
        ),
        O =
          null == v.hooks.getQueryParameters
            ? _objectSpread({}, S)
            : v.hooks.getQueryParameters(S),
        x = p.buildLinkUrl(O),
        I = h.LINK_CLIENT_CORS_ORIGIN;
      null != v.hooks.updateLinkURL &&
        ((x = v.hooks.updateLinkURL(x, S)), (I = v.hooks.updateLinkURL(I, S)));
      var P = function performOpen(t) {
          p.sendMessage(m, I)(_objectSpread({action: "open"}, t));
        },
        T = function hideViewport() {
          (S.linkOpenId = p.uuid()), m.hide();
        },
        A = function sendHeartBeat() {
          var t = S.linkOpenId,
            r = S.env,
            o = S.token;
          if (null != t && (null != r || null != o))
            try {
              var i = _objectSpread(
                  _objectSpread({linkOpenId: t}, null != r && {env: r}),
                  null != o && {token: o}
                ),
                a = p.buildLinkUrl(i, {
                  LINK_CLIENT_STABLE_URL: h.LINK_CLIENT_STABLE_URL,
                  LINK_CLIENT_URL: h.LINK_CLIENT_URL,
                  LINK_HTML_PATH: h.LINK_OPEN_HTML_PATH,
                });
              null != v.hooks.updateLinkURL && (a = v.hooks.updateLinkURL(a, S)),
                null != v.hooks.emitLinkOpen
                  ? v.hooks.emitLinkOpen(a)
                  : (0, g.emitLinkOpen)(a);
            } catch (t) {}
          try {
            var u,
              c = new XMLHttpRequest(),
              l = (0, _.default)(null !== (u = S.env) && void 0 !== u ? u : "");
            (c.onerror = function () {}),
              c.open("POST", l + "/link/heartbeat", !0),
              c.setRequestHeader("Content-Type", "application/json"),
              c.send(JSON.stringify({a: !0, b: !0, link_open_id: t}));
          } catch (t) {}
        },
        R = {};
      R[h.PLAID_INTERNAL_NAMESPACE] = {
        exit: function exit(r) {
          "function" == typeof t.onExit && t.onExit(r.error, r.metadata),
            T(),
            (o = null);
        },
        event: function event(r) {
          "function" == typeof t.onEvent && t.onEvent(r.eventName, r.metadata);
        },
        connected: function connected(r) {
          t.onSuccess(r.metadata.public_token, r.metadata), T();
        },
        "ready-for-configure": function readyForConfigure() {
          p.sendMessage(m, I)({action: "configure", config: S});
        },
        ready: function ready() {
          (q = !0),
            (G = null != o ? Date.now() - o : null),
            z(),
            "function" == typeof t.onLoad && t.onLoad();
        },
        resize: function resize(t) {
          null != t.height && null != m.resize && m.resize(t.height);
        },
      };
      for (
        var N = function _loop() {
            var o = (0, u.default)(C[L], 2),
              i = o[0];
            o[1].forEach(function (o) {
              R[i] = o(R[i] || {}, t, r, m);
            });
          },
          L = 0,
          C = Object.entries(v.messageHandlerExtensions);
        L < C.length;
        L++
      )
        N();
      for (var k = [], M = 0, j = Object.entries(R); M < j.length; M++) {
        var U = (0, u.default)(j[M], 2),
          W = U[0],
          D = U[1],
          V = p.createMessageEventListener(W, E, D);
        window.addEventListener("message", V, !1), k.push(V);
      }
      var K,
        B = function exit(r) {
          if (m.isOpen()) {
            var o = {config: r};
            (0, b.validateExitOptions)(t, r),
              p.sendMessage(m, I)(_objectSpread({action: "exit"}, o));
          }
        },
        H = !1,
        q = !1,
        z = function onReady() {},
        G = null;
      m.initialize(x, E);
      var Q = function open() {
          var t = arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : null;
          if (H)
            throw new Error(
              "Cannot call open() on Link handler that is already destroyed"
            );
          var r = t || S.institution;
          t && K !== r && ((S.institution = t || S.institution), (q = !1), m.refresh()),
            (K = r),
            m.show(),
            A();
          var i = Date.now(),
            a = null != o ? Date.now() - o : null;
          q
            ? P({
                institution: t,
                openStartedAt: i,
                createToOnLoadInterval: G,
                createToOpenInterval: a,
                linkOpenId: S.linkOpenId,
              })
            : (z = function onReady() {
                P({
                  institution: t,
                  openStartedAt: i,
                  createToOnLoadInterval: G,
                  createToOpenInterval: a,
                  linkOpenId: S.linkOpenId,
                });
              });
        },
        X = function submit(t) {
          var r = t;
          p.sendMessage(m, I)({action: "submit", data: r});
        },
        Y = function destroy() {
          (H = !0), m.destroy();
          for (var t = 0, r = k; t < r.length; t++) {
            var o = r[t];
            window.removeEventListener("message", o);
          }
        };
      return {exit: B, open: Q, submit: X, destroy: Y};
    };
  },
  function (t, r, o) {
    "use strict";
    o(1), Object.defineProperty(r, "__esModule", {value: !0}), (r.create = void 0);
    var i = o(231);
    r.create = function create() {
      var t = document.body.style.overflow,
        r = null,
        o = !1,
        a = null,
        u = function hide() {
          (o = !1),
            null != r && (r.style.display = "none"),
            (document.body.style.overflow = t),
            window.parent.focus(),
            null != a && a.focus();
        };
      return {
        initialize: function initialize(t, o) {
          ((r = document.createElement("iframe")).id = "plaid-link-iframe-".concat(o)),
            (r.title = "Plaid Link"),
            (r.src = t),
            (r.allow = "camera ".concat(i.LINK_IFRAME_FEATURE_POLICY_URLS, ";")),
            r.setAttribute("sandbox", i.LINK_IFRAME_SANDBOX_PERMISSIONS),
            (r.width = "100%"),
            (r.height = "100%"),
            (r.style.position = "fixed"),
            (r.style.top = "0"),
            (r.style.left = "0"),
            (r.style.right = "0"),
            (r.style.bottom = "0"),
            (r.style.zIndex = "9999999999"),
            (r.style.borderWidth = "0"),
            (r.style.display = "none"),
            (r.style.overflowX = "hidden"),
            (r.style.overflowY = "auto"),
            document.body.appendChild(r);
        },
        refresh: function refresh() {
          null != r && (r.src += "");
        },
        show: function show() {
          (o = !0),
            (t = document.body.style.overflow),
            (document.body.style.overflow = "hidden"),
            (a = document.activeElement),
            null != r &&
              ((r.style.display = "block"),
              null != r.contentWindow && r.contentWindow.focus());
        },
        hide: u,
        postMessage: function postMessage(t, o) {
          null != r && null != r.contentWindow && r.contentWindow.postMessage(t, o);
        },
        isOpen: function isOpen() {
          return !0 === o;
        },
        resize: function resize() {},
        destroy: function destroy() {
          var t;
          (u(), null != r) &&
            (null === (t = r.parentElement) || void 0 === t || t.removeChild(r),
            (r = null));
        },
      };
    };
  },
  function (t, r, o) {
    "use strict";
    o(1);
    var i = o(2);
    Object.defineProperty(r, "__esModule", {value: !0}),
      (r.create = void 0),
      o(75),
      o(37);
    var a = o(231),
      u = i(o(400)),
      c = "plaid-link-temporary-id",
      l = "plaid-link-iframe",
      d = "plaid-link-stylesheet",
      p = "html" + Array(9).join("#".concat(c)),
      v = "\n  "
        .concat(p, ",\n  ")
        .concat(
          p,
          " > body {\n    border: 0 !important;\n    height: 100% !important;\n    margin: 0 !important;\n    max-height: auto !important;\n    max-width: auto !important;\n    min-height: 0 !important;\n    min-width: 0 !important;\n    padding: 0 !important;\n    position: static !important;\n    width: auto !important;\n  }\n  "
        )
        .concat(p, " > body > * {\n    display: none !important;\n  }\n  ")
        .concat(p, " > body > .")
        .concat(
          l,
          " {\n    border: 0 !important;\n    height: auto !important;\n    min-height: 100% !important;\n    width: 100% !important;\n  }\n"
        );
    r.create = function create() {
      var t = null,
        r = !1,
        o = "",
        i = "",
        p = "",
        h = {x: 0, y: 0},
        y = null,
        _ = function hide() {
          (r = !1),
            t && t.style.setProperty("display", "none", "important"),
            (function restoreAllElements() {
              var t = document.getElementById(d);
              t && t.parentNode && t.parentNode.removeChild(t),
                (document.documentElement.id = o),
                document.documentElement.style.setProperty(i, p);
            })(),
            (function restoreScroll() {
              window.scrollTo(h.x, h.y);
            })(),
            window.parent.focus(),
            null != y && y.focus();
        };
      return {
        refresh: function refresh() {
          null != t && (t.src += "");
        },
        hide: _,
        initialize: function initialize(r, o) {
          ((t = document.createElement("iframe")).className = l),
            (t.title = "Plaid Link"),
            (t.id = "plaid-link-iframe-".concat(o)),
            (t.src = r),
            (t.allow = "camera ".concat(a.LINK_IFRAME_FEATURE_POLICY_URLS, ";")),
            t.setAttribute("sandbox", a.LINK_IFRAME_SANDBOX_PERMISSIONS),
            t.style.setProperty("display", "none", "important"),
            document.body.appendChild(t);
        },
        isOpen: function isOpen() {
          return !0 === r;
        },
        postMessage: function postMessage(r, o) {
          null != t && null != t.contentWindow && t.contentWindow.postMessage(r, o);
        },
        resize: function resize(t) {
          document.documentElement.style.setProperty("height", t, "important");
        },
        show: function show() {
          r ||
            ((r = !0),
            (y = document.activeElement),
            (function saveScroll() {
              h = {
                x: document.documentElement.scrollLeft,
                y: document.documentElement.scrollTop,
              };
            })(),
            (function hideAllElements() {
              (o = document.documentElement.id),
                (i = document.documentElement.style.getPropertyValue("height")),
                (p = document.documentElement.style.getPropertyPriority("height"));
              var t = document.createElement("style");
              (t.id = d), (t.textContent = v);
              var r = document.querySelector("head");
              null != r && r.appendChild(t), (document.documentElement.id = c);
            })(),
            window.scrollTo(0, 0),
            t &&
              ((0, u.default)().isIOSChrome &&
                setTimeout(function () {
                  document.body.style.setProperty(
                    "height",
                    window.innerHeight + "px",
                    "important"
                  );
                }, 100),
              t.style.setProperty("display", "block", "important"),
              t.contentWindow && t.contentWindow.focus()));
        },
        destroy: function destroy() {
          var r;
          (_(), null != t) &&
            (null === (r = t.parentElement) || void 0 === r || r.removeChild(t),
            (t = null));
        },
      };
    };
  },
  function (t, r, o) {
    var i = o(1502),
      a = o(1506),
      u = o(1507),
      c = o(1508);
    (t.exports = function _toConsumableArray(t) {
      return i(t) || a(t) || u(t) || c();
    }),
      (t.exports.__esModule = !0),
      (t.exports.default = t.exports);
  },
  function (t, r, o) {
    var i = o(1503),
      a = o(1403);
    (t.exports = function _arrayWithoutHoles(t) {
      if (i(t)) return a(t);
    }),
      (t.exports.__esModule = !0),
      (t.exports.default = t.exports);
  },
  function (t, r, o) {
    t.exports = o(1504);
  },
  function (t, r, o) {
    o(1505), (t.exports = o(323).Array.isArray);
  },
  function (t, r, o) {
    var i = o(405);
    i(i.S, "Array", {isArray: o(1145)});
  },
  function (t, r, o) {
    var i = o(1130),
      a = o(1146),
      u = o(1117);
    (t.exports = function _iterableToArray(t) {
      if ((void 0 !== i && null != t[a]) || null != t["@@iterator"]) return u(t);
    }),
      (t.exports.__esModule = !0),
      (t.exports.default = t.exports);
  },
  function (t, r, o) {
    var i = o(1117),
      a = o(1403);
    (t.exports = function _unsupportedIterableToArray(t, r) {
      if (t) {
        if ("string" == typeof t) return a(t, r);
        var o = Object.prototype.toString.call(t).slice(8, -1);
        return (
          "Object" === o && t.constructor && (o = t.constructor.name),
          "Map" === o || "Set" === o
            ? i(t)
            : "Arguments" === o || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(o)
            ? a(t, r)
            : void 0
        );
      }
    }),
      (t.exports.__esModule = !0),
      (t.exports.default = t.exports);
  },
  function (t, r) {
    (t.exports = function _nonIterableSpread() {
      throw new TypeError(
        "Invalid attempt to spread non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."
      );
    }),
      (t.exports.__esModule = !0),
      (t.exports.default = t.exports);
  },
  function (t, r, o) {
    "use strict";
    o(24), o(3), o(18), o(33), o(1);
    var i = o(495),
      a = o(591),
      u = o(590),
      c = o(664),
      l = o(493);
    Object.defineProperty(r, "__esModule", {value: !0}),
      (r.setUp = r.findScriptTag = r.extendMessageHandlers = void 0);
    var d = l(o(527)),
      p = l(o(588));
    o(25), o(58), o(152), o(153), o(154), o(55), o(44), o(37), o(75), o(27), o(52);
    var v = o(100);
    function ownKeys(t, r) {
      var o = i(t);
      if (a) {
        var c = a(t);
        r &&
          (c = c.filter(function (r) {
            return u(t, r).enumerable;
          })),
          o.push.apply(o, c);
      }
      return o;
    }
    function _objectSpread(t) {
      for (var r = 1; r < arguments.length; r++) {
        var o = null != arguments[r] ? arguments[r] : {};
        r % 2
          ? ownKeys(Object(o), !0).forEach(function (r) {
              (0, p.default)(t, r, o[r]);
            })
          : c
          ? Object.defineProperties(t, c(o))
          : ownKeys(Object(o)).forEach(function (r) {
              Object.defineProperty(t, r, u(o, r));
            });
      }
      return t;
    }

    r.findScriptTag = function findScriptTag() {
      for (
        var t = document.getElementsByTagName("script"), r = 0, o = t.length;
        r < o;
        r += 1
      ) {
        return t[r];
      }
      throw new Error("Failed to find script");
    };
    r.extendMessageHandlers = function extendMessageHandlers(t, r, o, i) {
      return _objectSpread(
        _objectSpread({}, t),
        {},
        {
          acknowledged: function acknowledged() {
            var t = document.getElementById(v.PLAID_LINK_BUTTON_ID);
            null != t && (t.disabled = !1);
          },
        }
      );
    };
    var h = new RegExp(
        "public-([a-z]+)-".concat(
          "[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}"
        )
      ),
      y = function traverse(t, r) {
        var o = function _loop(o) {
          "object" === (0, d.default)(t[o])
            ? traverse(t[o], function (t, i) {
                r([o].concat(t), i);
              })
            : r([o], t[o]);
        };
        for (var i in t) o(i);
      };
    r.setUp = function setUp(t, r) {
      var o = r.getAttribute("data-form-id");
      if (null != o) {
        var i = document.getElementById(o);
        if (null == i) throw new Error("Uncaught Error: Specify a valid data-form-id");
        var a = r.getAttribute("data-api-version"),
          u = r.getAttribute("data-client-name"),
          c = r.getAttribute("data-product"),
          l = r.getAttribute("data-key"),
          d = r.getAttribute("data-env"),
          p = "true" === r.getAttribute("data-select-account"),
          _ = r.getAttribute("data-token"),
          g = r.getAttribute("data-webhook"),
          b =
            null != r.getAttribute("data-longtail") ||
            null != r.getAttribute("data-long-tail") ||
            null,
          E = t.create({
            apiVersion: a,
            clientName: u,
            env: d,
            isSimpleIntegration: !0,
            key: l,
            longtail: b,
            onSuccess: function onSuccess(t, r) {
              y(r, function (t, r) {
                var o =
                  t[0] +
                  t
                    .slice(1)
                    .map(function (t) {
                      return "[".concat(t, "]");
                    })
                    .join("");
                i.appendChild(
                  (function createHiddenInput(t, r) {
                    var o = document.createElement("input");
                    return (o.type = "hidden"), (o.name = t), (o.value = r), o;
                  })(o, r)
                );
              }),
                i.submit();
            },
            product: c,
            selectAccount: p,
            token: _,
            webhook: g,
          }),
          m = document.createElement("button");
        (m.id = v.PLAID_LINK_BUTTON_ID),
          (m.textContent = (function isPublicToken(t) {
            return null != t && h.test(t);
          })(_)
            ? "Link your bank account"
            : "Relink your bank account"),
          (m.onclick = function (t) {
            t.preventDefault(), E.open();
          }),
          i.appendChild(m);
      }
    };
  },
  function (t, r, o) {
    "use strict";
    o(24), o(3), o(18), o(33), o(1);
    var i = o(495),
      a = o(591),
      u = o(590),
      c = o(664),
      l = o(493);
    Object.defineProperty(r, "__esModule", {value: !0}),
      (r.extendMessageHandlers = void 0);
    var d = l(o(588));
    function ownKeys(t, r) {
      var o = i(t);
      if (a) {
        var c = a(t);
        r &&
          (c = c.filter(function (r) {
            return u(t, r).enumerable;
          })),
          o.push.apply(o, c);
      }
      return o;
    }
    function _objectSpread(t) {
      for (var r = 1; r < arguments.length; r++) {
        var o = null != arguments[r] ? arguments[r] : {};
        r % 2
          ? ownKeys(Object(o), !0).forEach(function (r) {
              (0, d.default)(t, r, o[r]);
            })
          : c
          ? Object.defineProperties(t, c(o))
          : ownKeys(Object(o)).forEach(function (r) {
              Object.defineProperty(t, r, u(o, r));
            });
      }
      return t;
    }
    r.extendMessageHandlers = function extendMessageHandlers(t, r, o, i) {
      var a = !1;
      return _objectSpread(
        _objectSpread({}, t),
        {},
        {
          success: function success(t) {
            (a = !0), "function" == typeof r.onSuccess && r.onSuccess("", t.metadata);
          },
          exit: function exit(t) {
            "function" != typeof r.onExit || a || r.onExit(t.error, t.metadata),
              i.hide();
          },
          event: function event(t) {
            "function" == typeof r.onEvent && r.onEvent(t.event_name, t.metadata);
          },
        }
      );
    };
  },
  function (t, r, o) {
    "use strict";
    o(24), o(3), o(18), o(33), o(1);
    var i = o(495),
      a = o(591),
      u = o(590),
      c = o(664),
      l = o(493);
    Object.defineProperty(r, "__esModule", {value: !0}),
      (r.extendMessageHandlers = void 0);
    var d = l(o(588));
    function ownKeys(t, r) {
      var o = i(t);
      if (a) {
        var c = a(t);
        r &&
          (c = c.filter(function (r) {
            return u(t, r).enumerable;
          })),
          o.push.apply(o, c);
      }
      return o;
    }
    function _objectSpread(t) {
      for (var r = 1; r < arguments.length; r++) {
        var o = null != arguments[r] ? arguments[r] : {};
        r % 2
          ? ownKeys(Object(o), !0).forEach(function (r) {
              (0, d.default)(t, r, o[r]);
            })
          : c
          ? Object.defineProperties(t, c(o))
          : ownKeys(Object(o)).forEach(function (r) {
              Object.defineProperty(t, r, u(o, r));
            });
      }
      return t;
    }
    r.extendMessageHandlers = function extendMessageHandlers(t, r, o, i) {
      return _objectSpread(
        _objectSpread({}, t),
        {},
        {
          result: function result(t) {
            "function" == typeof r.onResult && r.onResult(t.incremental_result);
          },
        }
      );
    };
  },
  function (t, r, o) {
    "use strict";
    o(24), o(3), o(18), o(33), o(1);
    var i = o(527),
      a = o(495),
      u = o(591),
      c = o(590),
      l = o(664),
      d = o(1118),
      p = o(493);
    Object.defineProperty(r, "__esModule", {value: !0}), (r.default = void 0);
    var v = p(o(588)),
      h = (function _interopRequireWildcard(t, r) {
        if (!r && t && t.__esModule) return t;
        if (null === t || ("object" !== i(t) && "function" != typeof t))
          return {default: t};
        var o = _getRequireWildcardCache(r);
        if (o && o.has(t)) return o.get(t);
        var a = {},
          u = Object.defineProperty && c;
        for (var l in t)
          if ("default" !== l && Object.prototype.hasOwnProperty.call(t, l)) {
            var d = u ? c(t, l) : null;
            d && (d.get || d.set) ? Object.defineProperty(a, l, d) : (a[l] = t[l]);
          }
        (a.default = t), o && o.set(t, a);
        return a;
      })(o(1179)),
      y = o(380),
      _ = p(o(1513)),
      g = p(o(1514)),
      b = o(100);
    function _getRequireWildcardCache(t) {
      if ("function" != typeof d) return null;
      var r = new d(),
        o = new d();
      return (_getRequireWildcardCache = function _getRequireWildcardCache(t) {
        return t ? o : r;
      })(t);
    }
    function ownKeys(t, r) {
      var o = a(t);
      if (u) {
        var i = u(t);
        r &&
          (i = i.filter(function (r) {
            return c(t, r).enumerable;
          })),
          o.push.apply(o, i);
      }
      return o;
    }
    function _objectSpread(t) {
      for (var r = 1; r < arguments.length; r++) {
        var o = null != arguments[r] ? arguments[r] : {};
        r % 2
          ? ownKeys(Object(o), !0).forEach(function (r) {
              (0, v.default)(t, r, o[r]);
            })
          : l
          ? Object.defineProperties(t, l(o))
          : ownKeys(Object(o)).forEach(function (r) {
              Object.defineProperty(t, r, c(o, r));
            });
      }
      return t;
    }
    var E = function extendMessageHandlers(t, r, o, i) {
      var a,
        u = h.sendMessage(i),
        c = {chainId: b.MAINNET_HEX_CHAIN_ID, rpcUrl: b.CLOUDFLARE_ETH_MAINNET_URL};
      return _objectSpread(
        _objectSpread({}, t),
        {},
        {
          connected: function connected(r) {
            var a = o.web3ConnectorCache;
            if (a) {
              var u = a.getConnector();
              if (!u) throw new Error("Unexpected state, missing connector");
              u.getProvider().then(function (t) {
                if (!o.onProviderSuccess)
                  throw new Error("Unexpected state, missing onProviderSuccess");
                o.onProviderSuccess(t, r.metadata);
              }),
                i.hide();
            } else t.connected(r);
          },
          "web3-message": function web3MessageHandler(t) {
            a ||
              (a = (function getWeb3Bridge() {
                if (o.web3Bridge) {
                  var t = o.web3Bridge;
                  return {
                    then: function then(r) {
                      return r(t);
                    },
                  };
                }
                return (0, _.default)().then(function (t) {
                  return (0, g.default)().then(function (r) {
                    return (0, r.validateChainOptionAndChainInformation)(c), new t(c);
                  });
                });
              })()),
              a.then(function (r) {
                r.setMessageSender(u),
                  (r.viewport = i),
                  t.message !== y.Web3MessageToTopWindow.START_BRIDGE &&
                    r.handleWeb3Message(t);
              });
          },
        }
      );
    };
    r.default = E;
  },
  function (t, r, o) {
    "use strict";
    o.r(r),
      (r.default = function () {
        return Promise.all([o.e(0), o.e(2), o.e(10), o.e(11), o.e(48)])
          .then(o.t.bind(null, 1604, 7))
          .then(function (t) {
            return t.Web3Bridge;
          });
      });
  },
  function (t, r, o) {
    "use strict";
    o.r(r),
      (r.default = function () {
        return Promise.all([o.e(0), o.e(26)])
          .then(o.t.bind(null, 1602, 7))
          .then(function (t) {
            return {
              validateChainOptionAndChainInformation:
                t.validateChainOptionAndChainInformation,
            };
          });
      });
  },
  function (t, r, o) {
    "use strict";
    o(24), o(3), o(18), o(33), o(1);
    var i = o(527),
      a = o(495),
      u = o(591),
      c = o(590),
      l = o(664),
      d = o(1118),
      p = o(493);
    Object.defineProperty(r, "__esModule", {value: !0}), (r.createEmbedded = void 0);
    var v = p(o(1380)),
      h = p(o(588)),
      y = p(o(1516)),
      _ = _interopRequireWildcard(o(1179)),
      g = o(100),
      b = o(1400),
      E = _interopRequireWildcard(o(1518)),
      m = o(231),
      w = p(o(400)),
      S = o(1396),
      O = o(1180),
      x = o(1402),
      I = ["embeddedComponentConfiguration"];
    function _getRequireWildcardCache(t) {
      if ("function" != typeof d) return null;
      var r = new d(),
        o = new d();
      return (_getRequireWildcardCache = function _getRequireWildcardCache(t) {
        return t ? o : r;
      })(t);
    }
    function _interopRequireWildcard(t, r) {
      if (!r && t && t.__esModule) return t;
      if (null === t || ("object" !== i(t) && "function" != typeof t))
        return {default: t};
      var o = _getRequireWildcardCache(r);
      if (o && o.has(t)) return o.get(t);
      var a = {},
        u = Object.defineProperty && c;
      for (var l in t)
        if ("default" !== l && Object.prototype.hasOwnProperty.call(t, l)) {
          var d = u ? c(t, l) : null;
          d && (d.get || d.set) ? Object.defineProperty(a, l, d) : (a[l] = t[l]);
        }
      return (a.default = t), o && o.set(t, a), a;
    }
    function ownKeys(t, r) {
      var o = a(t);
      if (u) {
        var i = u(t);
        r &&
          (i = i.filter(function (r) {
            return c(t, r).enumerable;
          })),
          o.push.apply(o, i);
      }
      return o;
    }
    function _objectSpread(t) {
      for (var r = 1; r < arguments.length; r++) {
        var o = null != arguments[r] ? arguments[r] : {};
        r % 2
          ? ownKeys(Object(o), !0).forEach(function (r) {
              (0, h.default)(t, r, o[r]);
            })
          : l
          ? Object.defineProperties(t, l(o))
          : ownKeys(Object(o)).forEach(function (r) {
              Object.defineProperty(t, r, c(o, r));
            });
      }
      return t;
    }
    r.createEmbedded = function createEmbedded(t, r) {
      var o = arguments.length > 2 && void 0 !== arguments[2] ? arguments[2] : {},
        i = t.embeddedComponentConfiguration,
        a = (0, y.default)(t, I);
      (0, b.validateCreateOptions)(a);
      var u = _.getUniqueId(),
        c = "embedded_".concat(u),
        l = E.create(r),
        d = (0, x.validateEmbeddedComponentConfiguration)(i),
        p = _objectSpread(
          _objectSpread({}, a),
          {},
          {
            isEmbedded: !0,
            isEmbeddedLink: !0,
            isLinkInitialize: !0,
            useMockFingerprint: o.useMockFingerprint,
          },
          !0 === o.forceDarkMode && {forceDarkMode: o.forceDarkMode}
        ),
        h = _objectSpread({}, p);
      delete h.onEvent, delete h.onExit, delete h.onLoad, delete h.onSuccess;
      var P,
        T = (0, w.default)().isMobile,
        A = _objectSpread(
          {
            isMobile: T,
            uniqueId: c,
            origin: _.getWindowOrigin(),
            linkSdkVersion: m.LINK_WEB_SDK_VERSION,
            isLinkWebSdk: !0,
          },
          h
        ),
        R = {
          ready: function ready() {
            _.sendMessage(l)({action: "open"});
          },
          "ready-for-configure": function readyForConfigure() {
            _.sendMessage(l)({
              action: "configure",
              config:
                null != d ? _objectSpread({embeddedComponentConfiguration: d}, A) : A,
            });
          },
          "internal-event": function internalEvent(t) {
            var r = t.event.start_link.link_token_configuration,
              i = r.institution_id,
              u = r.embedded_workflow_session_id;
            null != P && P.destroy(),
              (o.embeddedWorkflowSessionId = u),
              (o.embeddedOpenLinkConfiguration = r.embedded_open_link_configuration),
              (P = (0, S.create)(a, o)).open(i);
          },
        },
        N = [],
        L = _.createMessageEventListener(O.PLAID_INTERNAL_NAMESPACE, c, R);
      window.addEventListener("message", L, !1), N.push(L);
      var C = function destroy() {
          l.destroy();
          for (var t = 0, r = N; t < r.length; t++) {
            var o = r[t];
            window.removeEventListener("message", o);
          }
          P && P.destroy();
        },
        k = _objectSpread(
          _objectSpread({}, A),
          {},
          {experimentVariants: (0, v.default)(a.experimentVariants), version: g.VERSION}
        ),
        M = _.buildLinkUrl(k);
      return l.initialize(M, c), {destroy: C};
    };
  },
  function (t, r, o) {
    var i = o(591),
      a = o(1517);
    (t.exports = function _objectWithoutProperties(t, r) {
      if (null == t) return {};
      var o,
        u,
        c = a(t, r);
      if (i) {
        var l = i(t);
        for (u = 0; u < l.length; u++)
          (o = l[u]),
            r.indexOf(o) >= 0 ||
              (Object.prototype.propertyIsEnumerable.call(t, o) && (c[o] = t[o]));
      }
      return c;
    }),
      (t.exports.__esModule = !0),
      (t.exports.default = t.exports);
  },
  function (t, r, o) {
    var i = o(495);
    (t.exports = function _objectWithoutPropertiesLoose(t, r) {
      if (null == t) return {};
      var o,
        a,
        u = {},
        c = i(t);
      for (a = 0; a < c.length; a++) (o = c[a]), r.indexOf(o) >= 0 || (u[o] = t[o]);
      return u;
    }),
      (t.exports.__esModule = !0),
      (t.exports.default = t.exports);
  },
  function (t, r, o) {
    "use strict";
    o(1), Object.defineProperty(r, "__esModule", {value: !0}), (r.create = void 0);
    var i = o(231);
    r.create = function create(t) {
      var r = null;
      return {
        refresh: function refresh() {
          null != r && (r.src += "");
        },
        initialize: function initialize(o, a) {
          ((r = document.createElement("iframe")).id =
            "plaid-embedded-link-iframe-".concat(a)),
            (r.title = "Plaid Link"),
            (r.src = o),
            (r.allow = "".concat(i.LINK_IFRAME_FEATURE_POLICY_URLS, ";")),
            (r.width = "100%"),
            (r.height = "100%"),
            (r.style.borderWidth = "0"),
            t.replaceChildren.apply(t, [r]);
        },
        show: function show() {},
        hide: function hide() {},
        postMessage: function postMessage(t, o) {
          null != r && null != r.contentWindow && r.contentWindow.postMessage(t, o);
        },
        isOpen: function isOpen() {
          return !0;
        },
        resize: function resize() {},
        destroy: function destroy() {
          var t;
          null != r &&
            (null === (t = r.parentElement) || void 0 === t || t.removeChild(r),
            (r = null));
        },
      };
    };
  },
]);
