import Shell from '../components/layout/Shell.jsx';
import { GridContainer, Row, Col } from '../components/layout/Grid';
import '../components/layout/shell.css';
import '../components/layout/grid.css';
import './slot.css';
import { Card } from '../components/ui/Card.jsx';
import '../components/ui/card.css';

const Slot = ({ label }) => <div className="aa-slot">{label}</div>;

export default function Dashboard(){
  return (
    <Shell>
      <GridContainer>
           {/* Row 1: top 4 containers */}
          <Row minH={120}>

          <Col span={{base:12, md:6, lg:3}}>
          <Card variant="metric" title="Compliance Score">
          <div>92% <div className="aa-sub"> 4% vs last week (sample)</div>
          </div>
          </Card></Col>

          <Col span={{base:12, md:6, lg:3}}>
          <Card variant="metric" title="Failed Checks">
           <div>92% <div className="aa-sub"> 4% vs last week (sample)</div>
          </div>
         </Card></Col>

          <Col span={{base:12, md:6, lg:3}}>
          <Card variant="metric" title="Last Scan">
           <div>92% <div className="aa-sub"> 4% vs last week (sample)</div>
          </div>
         </Card></Col>

          <Col span={{base:12, md:6, lg:3}}>
          <Card variant="metric" title="Total Controls">
           <div>92% <div className="aa-sub"> 4% vs last week (sample)</div>
          </div>
         </Card></Col>

        </Row>
        {/* Row 2: big left + right rail */}
        <Row minH={340}>
          <Col span={{base:12, lg:8}}><Slot label="Chart area" /></Col>
          <Col span={{base:12, lg:4}}><Slot label="Right rail" /></Col>
        </Row>
        {/* Row 3: full-width table */}
        <Row minH={260}>
          <Col span={{base:12}}><Slot label="Table area" /></Col>
        </Row>
      </GridContainer>
    </Shell>
  );
}
