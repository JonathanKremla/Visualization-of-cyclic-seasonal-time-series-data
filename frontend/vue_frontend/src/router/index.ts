import { createRouter, createWebHistory } from 'vue-router'
import ManageData from '../components/ManageData.vue'
import LineAndCycleView from '../components/LineAndCycleView.vue'
import LineAndSpiralPlotView from '../components/LineAndSpiralView.vue'
import CycleAndSpiralView from '../components/CycleAndSpiralView.vue'
import AllView from '../components/AllView.vue'


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'ManageData',
      component: ManageData,
    },
    {
      path: '/lineAndCyclePlot', 
      name: 'LinePlot',
      component: LineAndCycleView
    },      
    {
      path: '/cycleAndSpiralPlot', 
      name: 'LinePlot',
      component: CycleAndSpiralView
    },      
    {
      path: '/lineAndSpiralPlot',
      name: 'SpiralPlot',
      component: LineAndSpiralPlotView
    },
    {
      path: '/allViews',
      name: 'AllView',
      component: AllView
    },

  ]
})

export default router
