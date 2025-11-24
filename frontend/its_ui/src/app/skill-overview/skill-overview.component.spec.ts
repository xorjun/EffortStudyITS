import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SkillOverviewComponent } from './skill-overview.component';

describe('SkillOverviewComponent', () => {
  let component: SkillOverviewComponent;
  let fixture: ComponentFixture<SkillOverviewComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SkillOverviewComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SkillOverviewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
