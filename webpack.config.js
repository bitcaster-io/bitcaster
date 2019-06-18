const autoprefixer = require("autoprefixer");
const webpack = require("webpack");
const path = require("path");
// const fs = require("fs");
const ExtractTextPlugin = require("extract-text-webpack-plugin");
const CleanWebpackPlugin = require("clean-webpack-plugin");
const UglifyJSPlugin = require('uglifyjs-webpack-plugin');

const rel = path.resolve.bind(null, __dirname + "/src/bitcaster/web/assets/");
const outputDir = path.resolve.bind(null, __dirname + "/src/bitcaster/web/static/bitcaster/")();
const VERSION = require("./package.json").version;

var IS_PRODUCTION = false;
var WITH_CSS_SOURCEMAPS = true;

const loaders = {
    css: {
        loader: "css-loader",
        options: {
            sourceMap: WITH_CSS_SOURCEMAPS,
            minimize: IS_PRODUCTION,
            devtool: 'source-map',
        },
    },
    postcss: {
        loader: "postcss-loader",
        options: {
            sourceMap: WITH_CSS_SOURCEMAPS,
            minimize: IS_PRODUCTION,
            devtool: 'source-map',
            plugins: function (loader) {
                return [
                    autoprefixer({
                        browsers: ["last 2 versions"]
                    })
                ]
            }
        }
    },
    scss: {
        loader: "sass-loader",

        options: {
            indentedSyntax: true,
            sourceMap: WITH_CSS_SOURCEMAPS,
            minimize: IS_PRODUCTION,
            devtool: 'source-map',
            // includePaths: [path.resolve(__dirname, "./src")]
        }
    }
};
const optimization = {
    minimizer: [
        new UglifyJSPlugin({
            uglifyOptions: {
                compress: {
                    drop_console: true,
                }
            }
        })
    ]
};

module.exports = [
    {
        entry: {
            pwstrength: "./index",
        },
        context: rel("bitcaster/js/pwstrength"),
        module: {},
        plugins: [],
        resolve: {
            modules: [rel("."), "node_modules"],
            extensions: [".js"],
        },
        output: {
            path: outputDir,
            filename: "[name].js",
            libraryTarget: "window",
            library: "pwds",
            sourceMapFilename: "[name].js.map",
        },
        optimization:optimization
    },
    {
        entry: "select2",
        output: {
            path: outputDir,
            filename: "select2.js",
            libraryTarget: "window",
            // library: "$",
            // sourceMapFilename: "jquery.js.map",
        },
    },
    {
        entry: "jquery",
        output: {
            path: outputDir,
            filename: "jquery.js",
            libraryTarget: "window",
            library: "$",
            sourceMapFilename: "jquery.js.map",
        },
    },
    {
        entry: "js-cookie",
        output: {
            path: outputDir,
            filename: "js-cookie.js",
            libraryTarget: "window",
            library: "Cookies"
        },
    },
    {
        entry: {
            bitcaster: [rel("bitcaster/bitcaster")],
            // vendor: [rel("bitcaster/vendor")],
            theme: [rel("bitcaster/theme")],
            charts: [rel("bitcaster/charts")],
        }, // -entry
        context: rel("."),
        module: {
            noParse: [
                /pwstrength/
            ],
            rules: [
                {
                    test: /icons\/.*\.png$/i,
                    exclude: /(node_modules)/,
                    use: [{
                        loader: "file-loader",
                        options: {
                            outputPath: "images/icons",
                            name: "[name].[ext]"
                        },
                    }],
                },
                {
                    test: /\.(png|gif|jpg|ico)$/i,
                    exclude: /(node_modules|icons)/,
                    use: [{
                        loader: "file-loader",
                        options: {
                            // limit: 8000, // Convert images < 8kb to base64 strings
                            outputPath: "images",
                            name: "[name].[ext]"
                        },
                    }],
                },
                {
                    test: /.(ttf|otf|eot|svg|woff(2)?)(\?[a-z0-9#]+)?$/,
                    // exclude: /(node_modules)/,
                    use: [{
                        loader: "file-loader",
                        options: {
                            name: "[name].[ext]",
                            outputPath: "fonts",
                            // publicPath: '/static/dist/fonts/'       // override the default path
                        },
                    }],
                },
                {
                    test: /\.css$/,
                    use: ExtractTextPlugin.extract({
                        fallback: "style-loader",
                        use: [loaders.css, loaders.postcss]
                    })
                },
                {
                    test: /\.scss$/,
                    use: ExtractTextPlugin.extract({
                        fallback: ["style-loader"],

                        use: [loaders.css, loaders.postcss, loaders.scss]
                    })
                },
            ], // -rules
        }, // -module
        devtool: 'source-map',
        output: {
            filename: "[name].js",
            path: outputDir,
            // library: "[name]",
            // libraryTarget: 'window',
            // libraryExport: 'default'
            // publicPath: "/build"
        },
        plugins: [
            // new BundleTracker({filename: './webpack-stats.json'}),
            new webpack.IgnorePlugin(/^\.\/locale$/, /moment$/),
            new ExtractTextPlugin("[name].css"),
            new CleanWebpackPlugin(outputDir),
            new webpack.LoaderOptionsPlugin({
                minimize: true
            }),
            new webpack.ProvidePlugin({
                $: 'jquery',
                jQuery: 'jquery',
                'window.jQuery': 'jquery',
            }),
            // new webpack.ProvidePlugin({
            //     $: "jQuery",
            //     jQuery: "jQuery",
            //     Cookies: 'js-cookie/src/js.cookie.js'
            // }),
            new webpack.DefinePlugin({
                VERSION: JSON.stringify(require("./package.json").version)
            })
        ],
        externals: {},
        watch: false,
        watchOptions: {
            aggregateTimeout: 300,
            ignored: "/node_modules/",
            poll: 1000
        }
    }
];
