import { defineConfig } from 'vitepress'

// 内容仓浏览站：直接浏览 markdown 字谜库。
// 部署到 GitHub Pages 项目页（base /<repo>/）；不绑自定义域（分站才是 zimi.diuci.com）。
const base = process.env.SITE_BASE || '/chinese-character-riddle/'

export default defineConfig({
  base,
  lang: 'zh-CN',
  title: '字谜开源库',
  titleTemplate: ':title | 字谜开源库',
  description: '全网质量最高、收录最完整的开源字谜库。古典公版，注释解析 CC BY 4.0，按谜种/难度/标签分门别类。',

  themeConfig: {
    nav: [
      { text: '总览', link: '/' },
      { text: '索引', link: '/riddles/索引' },
      { text: '打印版', link: '/print' },
      { text: '数据来源', link: '/sources' },
      { text: '指南', link: '/guide' },
    ],

    // 侧栏按目录结构自动生成：riddles/<谜种>/<谜面>
    sidebar: 'auto',

    search: {
      provider: 'local',
      options: {
        detailedView: true,
        miniSearch: {
          searchOptions: {
            fuzzy: 0.2,
            prefix: true,
            boost: { title: 4, answer: 3 },
          },
        },
      },
    },

    outline: { level: [2, 3], label: '本页目录' },

    socialLinks: [
      { icon: 'github', link: 'https://github.com/diuci/chinese-character-riddle' },
    ],

    footer: {
      message: '古典谜面/谜底/解析属公有领域；我方原创当代谜、注释、解析与选篇编排 © 丢词大作战，采用 CC BY 4.0。',
      copyright: '内容来源与授权说明见「数据来源」。',
    },

    lastUpdated: true,
    docFooter: { prev: '上一篇', next: '下一篇' },
  },
})
