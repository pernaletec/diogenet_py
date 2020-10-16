const path = require("path");
const ForkTsCheckerWebpackPlugin = require("fork-ts-checker-webpack-plugin");
const { CleanWebpackPlugin } = require("clean-webpack-plugin");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const webpack = require("webpack");

const DIST = path.resolve(__dirname, "../diogenet_py/static/client");

const POLYFILLS = [];

function appendPolyfills(entries) {
    return entries.map(file => path.resolve(__dirname, file));
}

const ENTRIES = {
    map: appendPolyfills(["src/map.ts"]),
    horus: appendPolyfills(["src/horus.ts"]),

    main_styles: path.resolve(__dirname, "src/styles/main.ts"),
    map_styles: path.resolve(__dirname, "src/styles/map.ts"),
    horus_styles: path.resolve(__dirname, "src/styles/horus.ts"),
};

const AutoprefixerLoader = {
    loader: "postcss-loader",
    options: {
        plugins: () => [
            require("autoprefixer"),
        ],
    },
};

module.exports = {
    mode: "development",
    entry: ENTRIES,
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
            {
                test: /\.(sass|scss)$/,
                use: [
                    MiniCssExtractPlugin.loader,
                    "css-loader",
                    AutoprefixerLoader,
                    "sass-loader",
                ],
                exclude: /node_modules/,
            },
            {
                test: /\.css$/,
                use: [
                    MiniCssExtractPlugin.loader,
                    "css-loader",
                    AutoprefixerLoader,
                ],
                exclude: /node_modules/,
            },
            {
                test: /\.(png|jpg|ico|jpeg|gif|ttf|otf|eot|svg|woff(2)?)$/,
                use: [
                    "file-loader",
                ],
            },
        ],
    },
    resolve: {
        extensions: [
            ".tsx",
            ".ts",
            ".jsx",
            ".js",
            ".sass",
            ".scss",
            ".css",
        ],
    },
    devtool: "source-map",
    output: {
        filename: "[name].bundle.js",
        path: DIST,
    },
    plugins: [
        new ForkTsCheckerWebpackPlugin(),
        new CleanWebpackPlugin(),
        new MiniCssExtractPlugin({
            filename: "[name].bundle.css",
        }),
        new webpack.ProvidePlugin({
            $: "jquery",
            jquery: "jquery",
            jQuery: "jquery",
            "window.$": "jquery",
            "window.jQuery": "jquery",
            Popper: ["popper.js", "default"],
        }),
    ],
    devServer: {
        contentBase: DIST,
        compress: true,
        port: 9696,
    },
};
