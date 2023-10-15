# Omnifocus-export-markdown

Export Omnifocus 3 database into a Markdown file, compatible with [Obsidian](https://Obsidian.md)

## Usage

```
python3 omnifocus2md.py
```

## Exported results
Tasks within the same project will be exported into the same markdown file formatted as below, named after the `project name - project id.md`

```
---
status: inactive
url: omnifocus:///task/lMChPi-O7Mi
---
# [Pack list](omnifocus:///task/lMChPi-O7Mi)

- [ ] [洗面奶，面霜](omnifocus:///task/n8CUC5uouaq)

- [ ] [电脑 iPad](omnifocus:///task/bO01pPmiNjk)

- [ ] [充电器充电宝](omnifocus:///task/f56npLRrFSR)

- [ ] [Cat - 拉屎](omnifocus:///task/buJHNcUtZ2O)

- [ ] [Cat - 猫包，链子](omnifocus:///task/lwxt0fPpL9T)

- [ ] [牙刷牙膏](omnifocus:///task/k-aCrxV3m1n)

- [ ] [Cat - 碗，盖子](omnifocus:///task/n3GlXDhl3Rq)

- [ ] [充电线 c 和 lightning](omnifocus:///task/jaBkoODYrc1)

- [ ] [Cat - 食物，猫条](omnifocus:///task/eSAdrvsh_wX)
```

## Note

There is no hiearchy and order in the exported markdown file, because I just want to be able to search for tasks in plain text, task names and urls are all I need.

## For Updating

In order to update the exported markdown file, you can use [cron](https://crontab.guru/) or [Keyboard Maestro](http://www.keyboardmaestro.com/) to run the script periodically.
