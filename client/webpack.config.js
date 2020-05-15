const path = require("path");
const ForkTsCheckerWebpackPlugin = require("fork-ts-checker-webpack-plugin");
const { CleanWebpackPlugin } = require("clean-webpack-plugin");

const DIST = path.resolve(__dirname, "../diogenet_py/static");

const POLYFILLS = [];

const ENTRIES = [
    "src/main.ts"
].map(file => path.resolve(__dirname, file));

module.exports = {
    mode: "development",
    entry: POLYFILLS.concat(ENTRIES),
    module: {
        rules: [
            {
                test: /\.tsx?$/,
                use: [
                    "babel-loader",
                    {
                        loader: "ts-loader",
                        options: {
                            transpileOnly: true,
                        },
                    },
                ],
                exclude: /node_modules/,
            },
            {
                test: /\.jsx?$/,
                use: "babel-loader",
                exclude: /node_modules/,
            },
        ],
    },
    resolve: {
        extensions: [".tsx", ".ts", ".jsx", ".js"],
    },
    devtool: "source-map",
    output: {
        filename: "bundle.js",
        path: DIST,
    },
    plugins: [
        new ForkTsCheckerWebpackPlugin(),
        new CleanWebpackPlugin(),
    ],
    devServer: {
        contentBase: DIST,
        compress: true,
        port: 9696,
    },
};
