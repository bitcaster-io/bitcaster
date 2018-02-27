const autoprefixer = require("autoprefixer");
const webpack = require("webpack");
const path = require("path");
// const fs = require("fs");
const ExtractTextPlugin = require("extract-text-webpack-plugin");
const CleanWebpackPlugin = require("clean-webpack-plugin");

const rel = path.resolve.bind(null, __dirname + "/src/mercury/static/");
const outputDir = rel("dist");
const VERSION = require("./package.json").version;

const loaders = {
    css: {
        loader: "css-loader"
    },
    postcss: {
        loader: "postcss-loader",
        options: {
            plugins: (loader) => [
                autoprefixer({
                    browsers: ["last 2 versions"]
                })
            ]
        }
    },
    scss: {
        loader: "sass-loader",
        options: {
            indentedSyntax: true,
            // includePaths: [path.resolve(__dirname, "./src")]
        }
    }
};

module.exports = {
    context: rel("."),
    entry: {
        // app: [rel("bitcaster/index")],
        bitcaster: [rel("bitcaster/index")],
        vendor: [rel("bitcaster/vendor")]
    }, // -entry
    module: {
        rules: [
            {
                test: /\.(png|gif|jpg)$/i,
                exclude: /(node_modules)/,
                use: [{
                    loader: "file-loader",
                    options: {
                        outputPath: "images",
                    },
                }],
            },
            {
                test: /.(ttf|otf|eot|svg|woff(2)?)(\?[a-z0-9]+)?$/,
                exclude: /(node_modules)/,
                use: [{
                    loader: "file-loader",
                    options: {
                        name: "[name].[ext]",
                        outputPath: "fonts",
                        // publicPath: '/static/dist/fonts/'       // override the default path
                    },
                }],
            },
            // {
            //     test: /\.js$/,
            //     exclude: /node_modules/,
            //     use: ["babel-loader"]
            // },
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
                    fallback: "style-loader",
                    use: [loaders.css, loaders.postcss, loaders.scss]
                })
            }
        ]// -rules
    }, // -module
    output: {
        filename: "[name].js",
        path: outputDir
        // publicPath: "/build"
    },
    plugins: [
        // new BundleTracker({filename: './webpack-stats.json'}),

        new ExtractTextPlugin("[name].css"),
        new CleanWebpackPlugin(outputDir),
        new webpack.LoaderOptionsPlugin({
            minimize: true
        }),
        new webpack.ProvidePlugin({
            $: "jquery",
            jQuery: "jquery",
            Popper: 'popper.js'
        }),
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
};
